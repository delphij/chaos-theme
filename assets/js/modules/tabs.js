// Tabbed content panels (`> [!TAB]` blocks grouped by typeset-tabs.html).
//
// Progressive enhancement over server-rendered initial state: roving tabindex
// with arrow/Home/End navigation (selection follows focus), Find-in-Page
// synchronization via `beforematch` on `hidden="until-found"` panels,
// overflow detection with a native popover jump menu, and automatic group
// synchronization across `.tabs` sharing the same sorted set of tab titles
// (opt out with `.nogroup`, or override with `data-tab-group`).

function getTabList(container) {
  return container.querySelector(':scope > .tab-bar > .tab-list');
}

function getTabs(container) {
  const list = getTabList(container);
  return list ? Array.from(list.querySelectorAll(':scope > .tab-btn')) : [];
}

function getSyncKey(container) {
  if (container.classList.contains('nogroup')) return null;
  if (container.dataset.tabGroup) return `g:${container.dataset.tabGroup}`;
  const labels = getTabs(container).map((b) => b.textContent.trim()).sort();
  return labels.length ? `a:${labels.join('\0')}` : null;
}

function activateTab(container, index, { focus = false, sync = true } = {}) {
  const list = getTabList(container);
  const tabs = getTabs(container);
  const panels = Array.from(container.querySelectorAll(':scope > .tab-panel'));
  const menuItems = Array.from(container.querySelectorAll(':scope > .tab-bar > .tab-menu .tab-menu-item'));
  if (index < 0 || index >= tabs.length) return;

  tabs.forEach((btn, i) => {
    const active = i === index;
    btn.setAttribute('aria-selected', active ? 'true' : 'false');
    btn.tabIndex = active ? 0 : -1;
  });

  menuItems.forEach((item, i) => {
    item.setAttribute('aria-checked', i === index ? 'true' : 'false');
  });

  panels.forEach((panel, i) => {
    if (i === index) {
      panel.removeAttribute('hidden');
      panel.tabIndex = 0;
    } else {
      panel.hidden = 'until-found';
      panel.removeAttribute('tabindex');
    }
  });

  const activeBtn = tabs[index];
  if (focus) activeBtn.focus({ preventScroll: true });
  if (list && list.scrollWidth > list.clientWidth) {
    activeBtn.scrollIntoView({ block: 'nearest', inline: 'nearest', container: 'nearest' });
  }

  const key = sync ? getSyncKey(container) : null;
  if (key) {
    const label = activeBtn.textContent.trim();
    for (const other of document.querySelectorAll('.tabs')) {
      if (other === container || getSyncKey(other) !== key) continue;
      const otherTabs = getTabs(other);
      const match = otherTabs.findIndex((b) => b.textContent.trim() === label);
      if (match !== -1) activateTab(other, match, { focus: false, sync: false });
    }
  }
}

function positionMenuFallback(menu, trigger) {
  const gap = 4;
  const pad = 8;
  const tRect = trigger.getBoundingClientRect();
  const mRect = menu.getBoundingClientRect();
  let left = tRect.right - mRect.width;
  if (left < pad) left = Math.min(tRect.left, window.innerWidth - mRect.width - pad);
  left = Math.max(pad, Math.min(left, window.innerWidth - mRect.width - pad));

  let top = tRect.bottom + gap;
  if (top + mRect.height > window.innerHeight - pad && tRect.top - gap - mRect.height >= pad) {
    top = tRect.top - gap - mRect.height;
  }
  top = Math.max(pad, Math.min(top, window.innerHeight - mRect.height - pad));

  menu.style.left = `${left}px`;
  menu.style.top = `${top}px`;
}

export function initTabs() {
  const containers = document.querySelectorAll('.tabs');
  if (!containers.length) return;

  const hasPopover = 'popover' in HTMLElement.prototype;
  const hasInvoker = 'commandForElement' in HTMLButtonElement.prototype;
  const hasFocusGroup = 'focusGroup' in HTMLElement.prototype;
  const hasAnchorPos = CSS.supports('position-area', 'block-end');
  const hasScrollTimeline = CSS.supports('animation-timeline', 'scroll()');

  for (const container of containers) {
    const bar = container.querySelector(':scope > .tab-bar');
    const list = bar?.querySelector(':scope > .tab-list');
    if (!bar || !list) continue;
    const tabs = Array.from(list.querySelectorAll(':scope > .tab-btn'));
    const panels = Array.from(container.querySelectorAll(':scope > .tab-panel'));
    const moreBtn = bar.querySelector(':scope > .tab-more');
    const menu = bar.querySelector(':scope > .tab-menu');
    const menuList = menu?.querySelector(':scope > .tab-menu-list');
    const menuItems = menuList ? Array.from(menuList.querySelectorAll(':scope > .tab-menu-item')) : [];

    list.addEventListener('click', (e) => {
      const btn = e.target.closest('.tab-btn');
      if (!btn || !list.contains(btn)) return;
      const idx = tabs.indexOf(btn);
      if (idx !== -1) activateTab(container, idx);
    });

    list.addEventListener('keydown', (e) => {
      const idx = tabs.indexOf(document.activeElement);
      if (idx === -1) return;
      const rtl = getComputedStyle(list).direction === 'rtl';
      let next = -1;
      if (e.key === 'ArrowRight') next = (idx + (rtl ? -1 : 1) + tabs.length) % tabs.length;
      else if (e.key === 'ArrowLeft') next = (idx + (rtl ? 1 : -1) + tabs.length) % tabs.length;
      else if (e.key === 'Home') next = 0;
      else if (e.key === 'End') next = tabs.length - 1;
      if (next !== -1) {
        e.preventDefault();
        activateTab(container, next, { focus: true });
      }
    });

    // Browser Find-in-Page (`hidden="until-found"`) reveals a hidden panel:
    // synchronize the tablist selection and hide sibling panels.
    container.addEventListener('beforematch', (e) => {
      const panel = e.target.closest('.tab-panel');
      if (!panel) return;
      const idx = panels.indexOf(panel);
      if (idx !== -1) activateTab(container, idx, { focus: false, sync: false });
    });

    // Edge-fade fallback for browsers without CSS scroll-driven animations.
    if (!hasScrollTimeline && tabs.length > 1 && 'IntersectionObserver' in window) {
      const first = tabs[0];
      const last = tabs[tabs.length - 1];
      const fadeObserver = new IntersectionObserver((entries) => {
        for (const { target, intersectionRatio } of entries) {
          list.classList.toggle(target === first ? 'more-start' : 'more-end', intersectionRatio < 1);
        }
      }, { root: list, threshold: 1, rootMargin: '1px' });
      fadeObserver.observe(first);
      fadeObserver.observe(last);
    }

    // Overflow jump menu (native popover + ResizeObserver).
    if (moreBtn && menu && menuList && hasPopover) {
      let enterOnOpen = false;
      let pointerDown = false;
      const focusActiveMenuItem = () => {
        const active = menuItems.find((i) => i.getAttribute('aria-checked') === 'true') || menuItems[0];
        active?.focus({ preventScroll: true });
      };

      const updateOverflow = () => {
        const overflows = list.scrollWidth > bar.clientWidth + 1;
        moreBtn.hidden = !overflows;
        if (!overflows && menu.matches(':popover-open')) {
          menu.hidePopover();
        }
      };

      updateOverflow();
      if ('ResizeObserver' in window) {
        new ResizeObserver(updateOverflow).observe(bar);
      }
      document.fonts?.ready?.then(updateOverflow);

      moreBtn.addEventListener('pointerdown', () => {
        pointerDown = true;
      });

      if (!hasInvoker) {
        moreBtn.addEventListener('click', () => {
          if (!pointerDown) enterOnOpen = true;
          menu.togglePopover();
        });
      }

      moreBtn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          pointerDown = false;
          enterOnOpen = true;
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          pointerDown = false;
          enterOnOpen = true;
          if (!menu.matches(':popover-open')) {
            moreBtn.click();
          } else {
            focusActiveMenuItem();
          }
        }
      });

      menu.addEventListener('toggle', (e) => {
        const isOpen = e.newState === 'open';
        moreBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        if (isOpen) {
          if (!hasAnchorPos) positionMenuFallback(menu, moreBtn);
          if (enterOnOpen && !pointerDown) focusActiveMenuItem();
        }
        enterOnOpen = false;
        pointerDown = false;
      });

      menuList.addEventListener('click', (e) => {
        const item = e.target.closest('.tab-menu-item');
        if (!item || !menuList.contains(item)) return;
        const idx = Number(item.dataset.tabIndex);
        if (!Number.isNaN(idx)) {
          // Focus the tab before hiding the popover so popover focus
          // restoration does not override the newly selected tab.
          activateTab(container, idx, { focus: true });
          menu.hidePopover();
        }
      });

      menuList.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          menu.hidePopover();
          return;
        }
        if (hasFocusGroup) return;
        if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key)) return;
        const current = menuItems.indexOf(document.activeElement);
        if (current < 0) return;
        const next = e.key === 'Home'
          ? 0
          : e.key === 'End'
            ? menuItems.length - 1
            : (current + (e.key === 'ArrowUp' ? -1 : 1) + menuItems.length) % menuItems.length;
        e.preventDefault();
        menuItems[next]?.focus({ preventScroll: true });
      });

      if (!hasFocusGroup) {
        menuList.setAttribute('role', 'menu');
      }
    }
  }
}
