/* Prova Cangur — "Posa't a prova" (mode imatge)
   Cada pregunta es mostra com la imatge sencera del problema (enunciat + figura +
   opcions, tal com l'examen). L'alumne respon amb els botons A)–E). Correcció amb
   puntuació oficial (s'inicia amb 30 punts; encert +valor, error −¼, en blanc 0; 0–150).
   Llegeix /assets/data/prova-cangur-index.json i els JSON per examen. */
(function () {
  "use strict";
  var I18N = (document.documentElement.lang || "ca").slice(0, 2);
  var T = {
    ca: { pick_course: "Tria un curs", pick_model: "Tria una prova", random: "Prova a l'atzar",
      shuffle: "Barreja (30 preguntes a l'atzar del curs)", q: "Pregunta", pts: "punts",
      clear: "Deixar en blanc", submit: "Finalitzar la prova", confirm: "Encara tens preguntes sense respondre. Vols finalitzar igualment?",
      your: "La teva resposta", correct: "Correcta", blank: "En blanc", result: "La teva nota",
      score: "Puntuació Cangur (s'inicia amb 30 punts)", hits: "Encerts", errs: "Errors", blanks: "En blanc",
      pct: "% d'encerts", another: "Una altra prova", back: "Tornar", noexams: "Encara no hi ha proves per a aquest curs.",
      loading: "Carregant…", model: "Model", day: "Dia", start: "Començar", zoom: "Ampliar imatge", choose: "Tria la resposta" },
    es: { pick_course: "Elige un curso", pick_model: "Elige una prueba", random: "Prueba al azar",
      shuffle: "Mezcla (30 preguntas al azar del curso)", q: "Pregunta", pts: "puntos",
      clear: "Dejar en blanco", submit: "Finalizar la prueba", confirm: "Aún tienes preguntas sin responder. ¿Finalizar igualmente?",
      your: "Tu respuesta", correct: "Correcta", blank: "En blanco", result: "Tu nota",
      score: "Puntuación Cangur (empieza con 30 puntos)", hits: "Aciertos", errs: "Errores", blanks: "En blanco",
      pct: "% de aciertos", another: "Otra prueba", back: "Volver", noexams: "Todavía no hay pruebas para este curso.",
      loading: "Cargando…", model: "Modelo", day: "Día", start: "Empezar", zoom: "Ampliar imagen", choose: "Elige la respuesta" },
    en: { pick_course: "Pick a year", pick_model: "Pick a test", random: "Random test",
      shuffle: "Shuffle (30 random questions from this year)", q: "Question", pts: "points",
      clear: "Leave blank", submit: "Finish test", confirm: "Some questions are unanswered. Finish anyway?",
      your: "Your answer", correct: "Correct", blank: "Blank", result: "Your score",
      score: "Cangur score (starts at 30 points)", hits: "Correct", errs: "Wrong", blanks: "Blank",
      pct: "% correct", another: "Another test", back: "Back", noexams: "No tests for this year yet.",
      loading: "Loading…", model: "Model", day: "Day", start: "Start", zoom: "Enlarge image", choose: "Choose your answer" }
  };
  var L = T[I18N] || T.ca;
  var OPTS = ["A", "B", "C", "D", "E"];

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]; }); }
  function qparam(k) { return new URLSearchParams(location.search).get(k); }
  function fmt(sec) { sec = Math.max(0, sec); var m = Math.floor(sec / 60), s = sec % 60; return m + ":" + (s < 10 ? "0" : "") + s; }

  function mapEj(e) {
    return { numero: e.numero, puntuacion: e.puntuacion, solucion: e.solucion, imagen: e.imagen, titulo: e.titulo };
  }

  /* ---- Lightbox (ampliar imatge, útil al mòbil) ---- */
  var lb;
  function lightbox(src) {
    if (!lb) {
      lb = el("div", "pt-lightbox");
      lb.addEventListener("click", function () { lb.classList.remove("open"); });
      document.body.appendChild(lb);
    }
    lb.innerHTML = '<img src="' + esc(src) + '" alt="">';
    lb.classList.add("open");
  }

  function Engine(root) { this.root = root; this.manifest = null; this.state = null; }

  Engine.prototype.boot = function () {
    var self = this;
    this.root.innerHTML = '<p class="pt-faint">' + L.loading + "</p>";
    fetch("/assets/data/prova-cangur-index.json").then(function (r) { return r.json(); }).then(function (m) {
      self.manifest = m;
      var id = qparam("id"), curso = qparam("curso"), mode = qparam("mode");
      if (id) return self.startById(id);
      if (curso && mode) return self.startByCourse(curso, mode);
      self.renderLauncher(curso);
    }).catch(function () { self.root.innerHTML = '<p class="pt-faint">' + L.loading + " ✗</p>"; });
  };

  /* -------------------------------------------------------- Launcher */
  Engine.prototype.renderLauncher = function (preCurso) {
    var self = this, m = this.manifest;
    this.root.innerHTML = "";
    var wrap = el("div", "pt-launcher");
    wrap.appendChild(el("h2", null, L.pick_course));
    var grid = el("div", "pt-course-grid");
    var ALL = ["5prim", "6prim", "1eso", "2eso", "3eso", "4eso", "1btl", "2btl"];
    var have = {}; m.courses.forEach(function (c) { have[c.curso] = c; });
    ALL.forEach(function (cu) {
      var c = have[cu];
      var lbl = c ? (c.label[I18N] || c.label.ca) : cu;
      var b = el("button", "pt-course", esc(lbl));
      if (!c) b.setAttribute("aria-disabled", "true");
      else b.addEventListener("click", function () { self.renderModels(c, wrap); });
      grid.appendChild(b);
    });
    wrap.appendChild(grid);
    wrap.appendChild(el("div", "pt-models-slot"));
    this.root.appendChild(wrap);
    if (preCurso && have[preCurso]) this.renderModels(have[preCurso], wrap);
  };

  Engine.prototype.renderModels = function (course, wrap) {
    var self = this;
    wrap.querySelectorAll(".pt-course").forEach(function (b) {
      b.classList.toggle("is-active", b.textContent === (course.label[I18N] || course.label.ca));
    });
    var slot = wrap.querySelector(".pt-models-slot"); slot.innerHTML = "";
    slot.appendChild(el("h2", null, L.pick_model + " — " + esc(course.label[I18N] || course.label.ca)));
    if (!course.models.length) { slot.appendChild(el("p", "pt-muted", L.noexams)); return; }
    var list = el("div", "pt-models");
    course.models.forEach(function (mod) {
      var sub = (mod.modelo === "24mar" || mod.modelo === "dia24") ? (L.day + " 24") :
                (mod.modelo === "19mar" ? (L.day + " 19") : (L.model + " " + mod.modelo));
      var b = el("button", "pt-model",
        '<span class="pt-model-ic">📝</span><span class="pt-model-main"><b>' + esc(sub) +
        '</b><span>' + mod.num_preguntas + " " + L.q.toLowerCase() + "s · " + (mod.tiempo_min || 75) + " min · " +
        esc(mod.fecha || "") + '</span></span><span class="pt-model-go">' + L.start + " →</span>");
      b.addEventListener("click", function () { self.startById(mod.id); });
      list.appendChild(b);
    });
    var rnd = el("button", "pt-model pt-special",
      '<span class="pt-model-ic">🎲</span><span class="pt-model-main"><b>' + esc(L.random) + '</b></span><span class="pt-model-go">→</span>');
    rnd.addEventListener("click", function () { self.startByCourse(course.curso, "aleatori"); });
    list.appendChild(rnd);
    if (course.models.length > 1) {
      var sh = el("button", "pt-model pt-special",
        '<span class="pt-model-ic">🔀</span><span class="pt-model-main"><b>' + esc(L.shuffle) + '</b></span><span class="pt-model-go">→</span>');
      sh.addEventListener("click", function () { self.startByCourse(course.curso, "barreja"); });
      list.appendChild(sh);
    }
    slot.appendChild(list);
    slot.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  /* -------------------------------------------------------- Loaders */
  Engine.prototype.startById = function (id) {
    var self = this;
    this.root.innerHTML = '<p class="pt-faint">' + L.loading + "</p>";
    fetch("/assets/data/ejercicios/" + id + ".json").then(function (r) { return r.json(); }).then(function (col) {
      self.begin({ titulo: col.titulo, tiempo: (col.prova_cangur && col.prova_cangur.tiempo_min) || 75 },
                 col.ejercicios.map(mapEj));
    });
  };

  Engine.prototype.startByCourse = function (curso, mode) {
    var self = this;
    var course = (this.manifest.courses || []).filter(function (c) { return c.curso === curso; })[0];
    if (!course || !course.models.length) { this.renderLauncher(curso); return; }
    if (mode === "aleatori") return this.startById(course.models[Math.floor(Math.random() * course.models.length)].id);
    this.root.innerHTML = '<p class="pt-faint">' + L.loading + "</p>";
    Promise.all(course.models.map(function (mm) { return fetch(mm.json).then(function (r) { return r.json(); }); }))
      .then(function (cols) {
        var pool = [];
        cols.forEach(function (col) { col.ejercicios.forEach(function (e) { pool.push(mapEj(e)); }); });
        for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
        var qs = pool.slice(0, 30); qs.forEach(function (q, k) { q.numero = k + 1; });
        self.begin({ titulo: L.shuffle, tiempo: 75 }, qs);
      });
  };

  /* -------------------------------------------------------- Test */
  Engine.prototype.begin = function (meta, questions) {
    this.state = { meta: meta, questions: questions, answers: {}, submitted: false, remaining: (meta.tiempo || 75) * 60 };
    this.renderTest(); this.startTimer(); window.scrollTo(0, 0);
  };

  Engine.prototype.startTimer = function () {
    var self = this, s = this.state;
    if (this._tick) clearInterval(this._tick);
    this._tick = setInterval(function () {
      if (s.submitted) { clearInterval(self._tick); return; }
      s.remaining--;
      var tEl = self.root.querySelector(".pt-timer");
      if (tEl) { tEl.textContent = "⏱ " + fmt(s.remaining); tEl.classList.toggle("warn", s.remaining <= 300 && s.remaining > 0); tEl.classList.toggle("over", s.remaining <= 0); }
      if (s.remaining <= 0) { clearInterval(self._tick); self.submit(true); }
    }, 1000);
  };

  Engine.prototype.renderTest = function () {
    var self = this, s = this.state;
    this.root.innerHTML = "";
    var bar = el("div", "pt-bar");
    bar.appendChild(el("span", "pt-bar-title", esc(s.meta.titulo)));
    bar.appendChild(el("span", "pt-progress", '<span id="pt-done">0</span>/' + s.questions.length));
    bar.appendChild(el("span", "pt-timer", "⏱ " + fmt(s.remaining)));
    this.root.appendChild(bar);

    s.questions.forEach(function (q) {
      var box = el("div", "pt-q"); box.dataset.n = q.numero;
      var head = el("div", "pt-q-head");
      head.appendChild(el("span", "pt-q-num", L.q + " " + q.numero));
      head.appendChild(el("span", "pt-q-pts", q.puntuacion + " " + L.pts));
      box.appendChild(head);
      // imatge sencera del problema (clic → ampliar)
      var fig = el("button", "pt-qfull-wrap"); fig.type = "button"; fig.title = L.zoom;
      var img = el("img", "pt-qfull"); img.loading = "lazy"; img.alt = L.q + " " + q.numero; img.src = q.imagen;
      fig.appendChild(img);
      fig.appendChild(el("span", "pt-zoom", "🔍"));
      fig.addEventListener("click", function () { lightbox(q.imagen); });
      box.appendChild(fig);
      // botons de resposta
      box.appendChild(el("div", "pt-choose", L.choose + ":"));
      var opts = el("div", "pt-opts");
      OPTS.forEach(function (o) {
        var b = el("button", "pt-opt"); b.dataset.o = o; b.innerHTML = o + ")";
        b.addEventListener("click", function () { self.choose(q.numero, o, box); });
        opts.appendChild(b);
      });
      var clr = el("button", "pt-clear", "✕ " + L.clear);
      clr.addEventListener("click", function () { self.choose(q.numero, null, box); });
      opts.appendChild(clr);
      box.appendChild(opts);
      box.appendChild(el("div", "pt-q-verdict"));
      self.root.appendChild(box);
    });

    var actions = el("div", "pt-actions");
    var sub = el("button", "pt-btn pt-btn-primary", L.submit);
    sub.addEventListener("click", function () { self.submit(false); });
    actions.appendChild(sub);
    var back = el("a", "pt-btn pt-btn-ghost", "← " + L.back); back.href = "?";
    actions.appendChild(back);
    this.root.appendChild(actions);
  };

  Engine.prototype.choose = function (n, o, box) {
    if (this.state.submitted) return;
    if (o === null) delete this.state.answers[n]; else this.state.answers[n] = o;
    box.querySelectorAll(".pt-opt").forEach(function (b) { b.classList.toggle("sel", b.dataset.o === o); });
    var d = this.root.querySelector("#pt-done"); if (d) d.textContent = Object.keys(this.state.answers).length;
  };

  /* -------------------------------------------------------- Scoring */
  Engine.prototype.submit = function (auto) {
    var s = this.state;
    if (s.submitted) return;
    if (!auto) { if (s.questions.length - Object.keys(s.answers).length > 0 && !confirm(L.confirm)) return; }
    s.submitted = true;
    if (this._tick) clearInterval(this._tick);
    var BASE = 30, score = BASE, hits = 0, errs = 0, blanks = 0, maxScore = BASE;
    s.questions.forEach(function (q) {
      maxScore += q.puntuacion;
      var a = s.answers[q.numero];
      if (a == null) blanks++;
      else if (a === q.solucion) { score += q.puntuacion; hits++; }
      else { score -= q.puntuacion / 4; errs++; }
    });
    if (score < 0) score = 0;
    this.renderResults({ score: score, hits: hits, errs: errs, blanks: blanks, maxScore: maxScore, n: s.questions.length });
    this.markReview();
  };

  Engine.prototype.markReview = function () {
    var s = this.state;
    this.root.querySelectorAll(".pt-q").forEach(function (box) {
      var n = +box.dataset.n;
      var q = s.questions.filter(function (x) { return x.numero === n; })[0];
      var a = s.answers[n];
      box.querySelectorAll(".pt-opt").forEach(function (b) {
        b.disabled = true;
        if (b.dataset.o === q.solucion) b.classList.add("ok");
        if (a && b.dataset.o === a && a !== q.solucion) b.classList.add("bad");
      });
      var v = box.querySelector(".pt-q-verdict");
      if (a == null) { v.className = "pt-q-verdict blank"; v.textContent = "○ " + L.blank + " · " + L.correct + ": " + q.solucion + ")"; }
      else if (a === q.solucion) { v.className = "pt-q-verdict ok"; v.textContent = "✓ " + L.correct + ": " + q.solucion + ")"; }
      else { v.className = "pt-q-verdict bad"; v.textContent = "✗ " + L.your + ": " + a + ") · " + L.correct + ": " + q.solucion + ")"; }
    });
  };

  Engine.prototype.renderResults = function (r) {
    var pct = Math.round((r.hits / r.n) * 100);
    var fillPct = Math.round((r.score / r.maxScore) * 100);
    var box = el("div", "pt-results");
    box.appendChild(el("div", "pt-score-sub", L.result));
    box.appendChild(el("div", "pt-score-big", (Math.round(r.score * 100) / 100) + " <span style='font-size:1.2rem;color:var(--text-faint)'>/ " + r.maxScore + "</span>"));
    box.appendChild(el("div", "pt-score-sub", L.score));
    var track = el("div", "pt-bar-track"); var fill = el("div", "pt-bar-fill"); fill.style.width = "0%"; track.appendChild(fill); box.appendChild(track);
    box.appendChild(el("div", "pt-faint", L.hits + ": " + r.hits + "/" + r.n + " (" + pct + "%)"));
    var stats = el("div", "pt-stats");
    function stat(v, l, cls) { var d = el("div", "pt-stat" + (cls ? " " + cls : "")); d.appendChild(el("div", "v", v)); d.appendChild(el("div", "l", l)); return d; }
    stats.appendChild(stat(r.hits, L.hits, "ok"));
    stats.appendChild(stat(r.errs, L.errs, "bad"));
    stats.appendChild(stat(r.blanks, L.blanks));
    stats.appendChild(stat(pct + "%", L.pct));
    box.appendChild(stats);
    var act = el("div", "pt-actions"); act.style.justifyContent = "center";
    var again = el("a", "pt-btn pt-btn-primary", "🔁 " + L.another); again.href = "?";
    act.appendChild(again);
    box.appendChild(act);
    this.root.insertBefore(box, this.root.firstChild);
    window.scrollTo({ top: 0, behavior: "smooth" });
    setTimeout(function () { fill.style.width = Math.max(0, fillPct) + "%"; }, 80);
  };

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById("prova-test");
    if (root) new Engine(root).boot();
  });
})();
