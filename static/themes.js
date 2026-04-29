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
        for (var i = 0; i < n; i++) {
            var l = el('div', 'vesak-lantern');
            l.textContent = icons[i % icons.length];
            // evenly spaced: one per column, random within that column
            l.style.left              = (i * colW + rand(colW * 0.15, colW * 0.85)) + '%';
            l.style.top               = rand(14, 62) + '%';
            l.style.fontSize          = rand(1.3, 2.1) + 'em';
            l.style.animationDuration = rand(3, 6) + 's';
            l.style.animationDelay    = rand(0, 4) + 's';
            overlay.appendChild(l);
        }
    }

    function createCrescent() {
        var c = document.createElement('div');
        c.className = 'crescent';
        c.textContent = '☪';
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
        var icons = ['🌸', '🌺', '🌼', '🌷'];
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

    function createStreamers(n) {
        n = n || 40;
        var colors = ['#ffd700','#ff4444','#ffffff','#4488ff'];
        for (var i = 0; i < n; i++) {
            var s = el('div', 'streamer');
            s.style.left               = rand(0, 100) + '%';
            s.style.background         = colors[Math.floor(Math.random() * colors.length)];
            s.style.animationDuration  = rand(5, 11) + 's';
            s.style.animationDelay     = rand(0, 9)  + 's';
            overlay.appendChild(s);
        }
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
            createStreamers(40);
            break;

        case 'hindu':
            createStars(50, 'hindu-star');
            break;

        case 'christian':
            createShimmer(60);
            break;

        case 'public_holiday':
            // colour shift only — no particles
            break;
    }

    // ── holiday name badge injected via Jinja (base.html) ────────────────────
    // badge is already rendered server-side; nothing to do here.

}());
