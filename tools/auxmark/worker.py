#!/usr/bin/env python3
# Copyright 2025 The Hugo Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Worker pool with per-domain rate limiting for auxmark.

Provides concurrent job execution while respecting rate limits per domain.
"""

import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable
from urllib.parse import urlparse

from .core import BaseModule, Job


def extract_domain_from_job(job: Job) -> str:
    """
    Extract domain from job metadata for rate limiting.

    Args:
        job: Job object containing metadata

    Returns:
        Domain name, or special key for local/unknown operations
    """
    # Try to extract URL from common metadata fields
    url = None

    # Image localizer: look for images list
    if 'images' in job.metadata:
        images = job.metadata['images']
        if images and isinstance(images, list) and len(images) > 0:
            url = images[0].get('url')

    # Tweet downloader: construct URL from tweet_id
    elif 'tweet_id' in job.metadata:
        tweet_id = job.metadata['tweet_id']
        url = f'https://publish.x.com/oembed?url=https://x.com/i/status/{tweet_id}'

    # Generic: check for 'url' field
    elif 'url' in job.metadata:
        url = job.metadata['url']

    if url:
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                return parsed.netloc
        except Exception:
            pass

    # Fallback for jobs without URLs
    return '__local__'


class RateLimitedWorkerPool:
    """
    Thread pool with per-domain rate limiting.

    Ensures only one request to a domain at a time, with configurable
    delay between requests to the same domain.
    """

    def __init__(self, max_workers: int = 4, rate_limit_delay: float = 1.0, verbose: bool = False):
        """
        Initialize worker pool.

        Args:
            max_workers: Maximum number of concurrent workers
            rate_limit_delay: Minimum delay between requests to same domain (seconds)
            verbose: Enable verbose logging
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.verbose = verbose

        # Per-domain locks and timestamps
        self._domain_locks: dict[str, threading.Lock] = {}
        self._last_request_time: dict[str, float] = {}
        self._domain_locks_lock = threading.Lock()  # Lock for the locks dict itself

    def _get_domain_lock(self, domain: str) -> threading.Lock:
        """
        Get or create a lock for a domain.

        Args:
            domain: Domain name

        Returns:
            Lock object for this domain
        """
        with self._domain_locks_lock:
            if domain not in self._domain_locks:
                self._domain_locks[domain] = threading.Lock()
            return self._domain_locks[domain]

    def _wait_for_rate_limit(self, domain: str) -> None:
        """
        Wait if needed to respect rate limit for domain.

        Args:
            domain: Domain name
        """
        with self._domain_locks_lock:
            last_time = self._last_request_time.get(domain)

        if last_time is not None:
            elapsed = time.time() - last_time
            if elapsed < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - elapsed
                if self.verbose:
                    print(f"  [Rate limit] Waiting {wait_time:.2f}s for {domain}", file=sys.stderr)
                time.sleep(wait_time)

    def _execute_with_rate_limit(
        self,
        job: Job,
        module: BaseModule,
        domain: str
    ) -> bool:
        """
        Execute job with per-domain rate limiting.

        Args:
            job: Job to execute
            module: Module to execute job with
            domain: Domain for rate limiting

        Returns:
            Result from module.preprocess()
        """
        # Acquire domain lock (ensures only one request to this domain at a time)
        lock = self._get_domain_lock(domain)

        with lock:
            # Wait if needed to respect rate limit
            self._wait_for_rate_limit(domain)

            # Execute job
            result = module.preprocess(job)

            # Update last request time for this domain
            with self._domain_locks_lock:
                self._last_request_time[domain] = time.time()

            return result

    def submit_job(self, job: Job, module: BaseModule) -> Future:
        """
        Submit a job to the worker pool.

        Args:
            job: Job to execute
            module: Module to execute job with

        Returns:
            Future object representing the job
        """
        domain = extract_domain_from_job(job)

        if self.verbose:
            print(f"  [Worker pool] Submitting job for {domain}: {job.file_path}:{job.line_no}", file=sys.stderr)

        return self.executor.submit(
            self._execute_with_rate_limit,
            job,
            module,
            domain
        )

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the worker pool.

        Args:
            wait: If True, wait for all jobs to complete
        """
        self.executor.shutdown(wait=wait)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)
