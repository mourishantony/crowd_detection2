/**
 * IPS Tech Community Custom Dialogs
 * Replaces browser alert() and confirm() with styled modals.
 */

(function () {
    // ── Inject dialog HTML once ──────────────────────────────────────
    function ensureContainer() {
        if (document.getElementById('IPS Tech Community-dialog-container')) return;
        const div = document.createElement('div');
        div.id = 'IPS Tech Community-dialog-container';
        div.innerHTML = `
            <!-- Alert Dialog -->
            <div class="ph-overlay" id="ph-alert-overlay">
                <div class="ph-dialog">
                    <div class="ph-dialog-icon" id="ph-alert-icon"></div>
                    <h3 class="ph-dialog-title" id="ph-alert-title">Notice</h3>
                    <p class="ph-dialog-msg" id="ph-alert-msg"></p>
                    <div class="ph-dialog-actions">
                        <button class="ph-btn ph-btn-primary" id="ph-alert-ok">OK</button>
                    </div>
                </div>
            </div>
            <!-- Confirm Dialog -->
            <div class="ph-overlay" id="ph-confirm-overlay">
                <div class="ph-dialog">
                    <div class="ph-dialog-icon ph-icon-warn">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    </div>
                    <h3 class="ph-dialog-title" id="ph-confirm-title">Confirm</h3>
                    <p class="ph-dialog-msg" id="ph-confirm-msg"></p>
                    <div class="ph-dialog-actions">
                        <button class="ph-btn ph-btn-outline" id="ph-confirm-cancel">Cancel</button>
                        <button class="ph-btn ph-btn-danger" id="ph-confirm-ok">Delete</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(div);
    }

    // ── IPS Tech CommunityAlert ─────────────────────────────────────────────────
    window.IPS Tech CommunityAlert = function (message, type) {
        ensureContainer();
        type = type || 'error'; // 'error', 'success', 'info'

        const overlay = document.getElementById('ph-alert-overlay');
        const msgEl   = document.getElementById('ph-alert-msg');
        const iconEl  = document.getElementById('ph-alert-icon');
        const okBtn   = document.getElementById('ph-alert-ok');
        const titleEl = document.getElementById('ph-alert-title');

        const config = {
            error:   { title: 'Error',   iconClass: 'ph-icon-error',   btnClass: 'ph-btn-danger',  icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>' },
            success: { title: 'Success', iconClass: 'ph-icon-success', btnClass: 'ph-btn-success', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' },
            info:    { title: 'Info',    iconClass: 'ph-icon-info',    btnClass: 'ph-btn-primary', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>' },
        };

        const c = config[type] || config.error;
        iconEl.className  = 'ph-dialog-icon ' + c.iconClass;
        iconEl.innerHTML  = c.icon;
        titleEl.textContent = c.title;
        okBtn.className   = 'ph-btn ' + c.btnClass;
        msgEl.textContent = message;

        overlay.classList.add('show');

        return new Promise(resolve => {
            function close() {
                overlay.classList.remove('show');
                okBtn.removeEventListener('click', close);
                resolve();
            }
            okBtn.addEventListener('click', close);
            overlay.addEventListener('click', e => { if (e.target === overlay) close(); }, { once: true });
        });
    };

    // ── IPS Tech CommunityConfirm ───────────────────────────────────────────────
    window.IPS Tech CommunityConfirm = function (message, okLabel) {
        ensureContainer();
        const overlay  = document.getElementById('ph-confirm-overlay');
        const msgEl    = document.getElementById('ph-confirm-msg');
        const okBtn    = document.getElementById('ph-confirm-ok');
        const cancelBtn = document.getElementById('ph-confirm-cancel');

        msgEl.textContent = message;
        okBtn.textContent = okLabel || 'Delete';
        overlay.classList.add('show');

        return new Promise(resolve => {
            function close(result) {
                overlay.classList.remove('show');
                okBtn.removeEventListener('click', onOk);
                cancelBtn.removeEventListener('click', onCancel);
                resolve(result);
            }
            function onOk() { close(true); }
            function onCancel() { close(false); }
            okBtn.addEventListener('click', onOk);
            cancelBtn.addEventListener('click', onCancel);
            overlay.addEventListener('click', e => { if (e.target === overlay) close(false); }, { once: true });
        });
    };

    // ── Intercept forms using onsubmit confirm() ─────────────────────
    // Replaces data-confirm attribute forms
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('form[data-confirm]').forEach(form => {
            form.addEventListener('submit', async e => {
                e.preventDefault();
                const msg = form.dataset.confirm;
                const label = form.dataset.confirmLabel || 'Delete';
                const ok = await IPS Tech CommunityConfirm(msg, label);
                if (ok) form.submit();
            });
        });
    });
})();
