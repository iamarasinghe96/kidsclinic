(function () {
    'use strict';

    var theme   = document.body.dataset.theme   || 'default';
    var holiday = document.body.dataset.holiday || '';

    if (theme === 'default') return;

    // Full-screen overlay — pointer-events:none so clicks pass through
    var overlay = document.createElement('div');
    overlay.id = 'theme-overlay';
    document.body.appendChild(overlay);

    // ── helpers ─────────────────────────────────────────────────────────────
    function rand(min, max) { return Math.random() * (max - min) + min; }

    function el(tag, cls) {
        var e = document.createElement(tag);
        if (cls) e.className = cls;
        return e;
    }

    // ── creators ────────────────────────────────────────────────────────────

    function createSnow(n) {
        n = n || 60;
        var flakes = ['❄', '❅', '❆'];
        for (var i = 0; i < n; i++) {
            var f = el('div', 'snowflake');
            f.textContent = flakes[Math.floor(Math.random() * flakes.length)];
            f.style.left            = rand(0, 100) + '%';
            f.style.fontSize        = rand(0.7, 1.6) + 'em';
            f.style.animationDuration  = rand(6, 14) + 's';
            f.style.animationDelay     = rand(0, 12) + 's';
            f.style.opacity         = rand(0.6, 1);
            overlay.appendChild(f);
        }
    }

    function createMoon(bgGradient, glowColor) {
        var moon = document.createElement('div');
        moon.className = 'poya-moon';
        if (bgGradient) moon.style.background = bgGradient;
        document.body.appendChild(moon);
    }

    function createVesakMoon() {
        var moon = document.createElement('div');
        moon.className = 'vesak-moon';
        document.body.appendChild(moon);
    }

    function createLanterns(n) {
        n = n || 12;
        var icons = ['🏮', '🪔', '🏮', '🏮', '🪔', '🏮'];
        var colW = 100 / n;

        // Upper/mid spread — one per column for even distribution
        for (var i = 0; i < n; i++) {
            var l = el('div', 'vesak-lantern');
            l.textContent = icons[i % icons.length];
            l.style.left              = (i * colW + rand(colW * 0.15, colW * 0.85)) + '%';
            l.style.top               = rand(14, 62) + '%';
            l.style.fontSize          = rand(1.3, 2.1) + 'em';
            l.style.animationDuration = rand(3, 6) + 's';
            l.style.animationDelay    = rand(0, 4) + 's';
            overlay.appendChild(l);
        }

        // Extra lanterns in the lower content area
        var lowerIcons = ['🏮', '🪔', '🕯', '🏮', '🪔', '🕯', '🏮', '🏮'];
        var nLower = 10;
        var colW2 = 100 / nLower;
        for (var j = 0; j < nLower; j++) {
            var l2 = el('div', 'vesak-lantern');
            l2.textContent = lowerIcons[j % lowerIcons.length];
            l2.style.left              = (j * colW2 + rand(colW2 * 0.1, colW2 * 0.9)) + '%';
            l2.style.top               = rand(65, 93) + '%';
            l2.style.fontSize          = rand(1.0, 1.8) + 'em';
            l2.style.animationDuration = rand(4, 7) + 's';
            l2.style.animationDelay    = rand(0, 5) + 's';
            overlay.appendChild(l2);
        }
    }

    function createCrescent() {
        var uid = 'im' + Math.floor(Math.random() * 1e6);
        var c = document.createElement('div');
        c.className = 'crescent';
        c.innerHTML =
            '<svg width="52" height="48" viewBox="0 0 52 48" xmlns="http://www.w3.org/2000/svg">' +
            '<defs><mask id="' + uid + '">' +
            '<rect width="52" height="48" fill="white"/>' +
            '<circle cx="24" cy="22" r="13" fill="black"/>' +
            '</mask></defs>' +
            '<circle cx="18" cy="24" r="16" fill="#ffd700" mask="url(#' + uid + ')"/>' +
            '<polygon fill="#ffd700" points="40,6 42,11.2 47.6,11.5 43.3,15.1 44.7,20.5 40,17.5 35.3,20.5 36.7,15.1 32.4,11.5 38,11.2"/>' +
            '</svg>';
        document.body.appendChild(c);
    }

    function createStars(n, cls) {
        n   = n   || 40;
        cls = cls || 'star';
        var icons = ['✦', '✧', '★', '·'];
        for (var i = 0; i < n; i++) {
            var s = el('div', cls);
            s.textContent = icons[Math.floor(Math.random() * icons.length)];
            s.style.left               = rand(0, 100) + '%';
            s.style.top                = rand(5, 95)  + '%';
            s.style.fontSize           = rand(0.5, 1.2) + 'em';
            s.style.animationDuration  = rand(1.5, 4) + 's';
            s.style.animationDelay     = rand(0, 3)   + 's';
            overlay.appendChild(s);
        }
    }

    function createPetals(n) {
        n = n || 50;
        // Sinhala/Tamil New Year: kavum, kokis, and non-rose flowers
        var icons = ['🥮', '🍪', '🌸', '🌼', '🌻', '🌸', '🌼'];
        for (var i = 0; i < n; i++) {
            var p = el('div', 'petal');
            p.textContent = icons[Math.floor(Math.random() * icons.length)];
            p.style.left               = rand(0, 100) + '%';
            p.style.fontSize           = rand(0.8, 1.5) + 'em';
            p.style.animationDuration  = rand(7, 15) + 's';
            p.style.animationDelay     = rand(0, 12) + 's';
            overlay.appendChild(p);
        }
    }

    function createDiyas(n) {
        n = n || 30;
        var colors = ['#ff6a00','#ff0080','#ffe100','#00e5ff','#7cff00'];
        for (var i = 0; i < n; i++) {
            var d = document.createElement('div');
            d.className = 'diya-light';
            d.style.left               = (i / n * 100) + '%';
            d.style.animationDuration  = rand(1.5, 3.5) + 's';
            d.style.animationDelay     = rand(0, 2.5) + 's';
            d.style.background         = colors[i % colors.length];
            document.body.appendChild(d);
        }
    }

    function createSun() {
        var sun = document.createElement('div');
        sun.className = 'pongal-sun';
        sun.textContent = '☀';
        document.body.appendChild(sun);
    }

    function createFlag() {
        var f = document.createElement('div');
        f.className = 'independence-flag';
        f.innerHTML =
            '<svg width="58" height="38" viewBox="0 0 58 38" xmlns="http://www.w3.org/2000/svg">' +
            // Gold outer border
            '<rect width="58" height="38" rx="3" fill="#FAC80A"/>' +
            // Saffron stripe
            '<rect x="2.5" y="2.5" width="9" height="33" fill="#E88200"/>' +
            // Green stripe
            '<rect x="11.5" y="2.5" width="9" height="33" fill="#00843D"/>' +
            // Maroon field
            '<rect x="20.5" y="2.5" width="35" height="33" fill="#8D153A"/>' +
            // Bo leaves — diamond shapes in each corner of the maroon area
            '<polygon points="24,6.5 26,8.5 24,10.5 22,8.5" fill="#FAC80A"/>' +
            '<polygon points="52,6.5 54,8.5 52,10.5 50,8.5" fill="#FAC80A"/>' +
            '<polygon points="24,27.5 26,29.5 24,31.5 22,29.5" fill="#FAC80A"/>' +
            '<polygon points="52,27.5 54,29.5 52,31.5 50,29.5" fill="#FAC80A"/>' +
            // Sword (vertical)
            '<rect x="36" y="10" width="2" height="18" rx="1" fill="#FAC80A"/>' +
            // Lion head
            '<circle cx="37" cy="14" r="4" fill="#FAC80A"/>' +
            // Lion body
            '<rect x="33" y="17" width="8" height="7" rx="2" fill="#FAC80A"/>' +
            // Tail
            '<path d="M41 22 Q47 18 45 12" stroke="#FAC80A" stroke-width="1.5" fill="none" stroke-linecap="round"/>' +
            '</svg>';
        document.body.appendChild(f);
    }

    function createShimmer(n) {
        n = n || 60;
        for (var i = 0; i < n; i++) {
            var d = el('div', 'shimmer-dot');
            d.style.left               = rand(0, 100) + '%';
            d.style.top                = rand(0, 100) + '%';
            d.style.animationDuration  = rand(2, 5) + 's';
            d.style.animationDelay     = rand(0, 4) + 's';
            overlay.appendChild(d);
        }
    }

    // ── dispatch ─────────────────────────────────────────────────────────────
    switch (theme) {
        case 'christmas':
            createSnow(60);
            break;

        case 'poya':
            createMoon();
            break;

        case 'vesak':
            createVesakMoon();
            createLanterns(12);
            break;

        case 'islamic':
            createCrescent();
            createStars(40, 'star');
            break;

        case 'new_year':
            createPetals(50);
            break;

        case 'deepavali':
            createDiyas(30);
            createStars(20, 'star');
            break;

        case 'pongal':
            createSun();
            break;

        case 'independence':
            createFlag();
            break;

        case 'hindu':
            createDiyas(30);
            createStars(20, 'star');
            break;

        case 'christian':
            createShimmer(60);
            createStars(40, 'star');
            break;

        case 'public_holiday':
            // colour shift only — no particles
            break;
    }

    // ── holiday name badge injected via Jinja (base.html) ────────────────────
    // badge is already rendered server-side; nothing to do here.

}());
