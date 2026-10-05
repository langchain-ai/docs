const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { test } = require("node:test");
const { runInNewContext } = require("node:vm");

const script = readFileSync(join(__dirname, "../src/changelog-navigation.js"), "utf8");
const PAGE = "/langsmith/self-hosted-changelog";

class Element {
  constructor(tagName, id = "", text = "") {
    this.tagName = tagName.toUpperCase();
    this.id = id;
    this.textContent = text;
    this.dataset = {};
    this.children = [];
    this.className = "";
    this.attributes = {};
    this.visible = true;
    this.replacements = 0;
    const classes = () => new Set(this.className.split(/\s+/).filter(Boolean));
    this.classList = {
      contains: (name) => classes().has(name),
      add: (name) => this.classList.toggle(name, true),
      remove: (name) => this.classList.toggle(name, false),
      toggle: (name, on) => {
        const names = classes();
        if (on) names.add(name);
        else names.delete(name);
        this.className = [...names].join(" ");
      },
    };
  }

  get firstChild() {
    return this.children[0] || null;
  }

  appendChild(child) {
    return this.insertBefore(child, null);
  }

  insertBefore(child, before) {
    child.parentElement = this;
    const index = before ? this.children.indexOf(before) : this.children.length;
    assert.notEqual(index, -1);
    this.children.splice(index, 0, child);
    return child;
  }

  replaceChildren(...children) {
    this.children.forEach((child) => { child.parentElement = null; });
    this.children = [];
    children.forEach((child) => this.appendChild(child));
    this.replacements++;
  }

  remove() {
    const parent = this.parentElement;
    parent.children.splice(parent.children.indexOf(this), 1);
    this.parentElement = null;
  }

  setAttribute(name, value) {
    this.attributes[name] = value;
  }

  getClientRects() {
    return this.visible ? [{}] : [];
  }
}

function setup({ path = PAGE, side = true, loading = false } = {}) {
  const root = new Element("html");
  root.dataset.currentPath = path;
  const content = root.appendChild(new Element("main", "content"));
  if (side) root.appendChild(new Element("div", "content-side-layout"));
  const all = () => {
    const walk = (node) => [node, ...node.children.flatMap(walk)];
    return walk(root);
  };
  const document = {
    documentElement: root,
    readyState: loading ? "loading" : "complete",
    createElement: (tag) => new Element(tag),
    getElementById: (id) => all().find((node) => node.id === id),
    querySelectorAll: (selector) => all().filter((node) =>
      selector === "h2[id]"
        ? node.tagName === "H2" && node.id
        : node.classList.contains(selector.slice(1)),
    ),
    addEventListener: (name, callback) => { assert.equal(name, "DOMContentLoaded"); ready = callback; },
  };
  let ready;
  let observer;
  const frames = [];
  runInNewContext(script, {
    document,
    requestAnimationFrame: (callback) => frames.push(callback),
    MutationObserver: class {
      constructor(callback) { observer = callback; }
      observe() {}
    },
  });
  const flush = () => {
    while (frames.length) frames.shift()();
  };
  const heading = (id, text = `\u200b${id.replace("langsmith-", "langsmith@").replaceAll("-", ".").replace("@", "-")}`) => {
    const update = content.appendChild(new Element("div"));
    const body = update.appendChild(new Element("div"));
    return body.appendChild(new Element("h2", id, text));
  };
  const links = (id = "changelog-chapters-sidebar") =>
    document.getElementById(id).children[1].children;
  return { root, content, document, heading, links, flush, frames, notify: () => observer(), ready: () => ready() };
}

test("indexes only visible exact minor chapters, leaving patches and categories untouched", () => {
  const dom = setup();
  const chapters = [dom.heading("langsmith-0-16-0", "\u200blangsmith-0.16.0"), dom.heading("langsmith-0-15-0", " langsmith-0.15.0 ")];
  const excluded = ["langsmith-0-15-1", "langsmith-0-16-0-rc-2", "v0-15", "release-cadence", "new-features"].map((id) => dom.heading(id));
  const patch = excluded[0];
  const download = patch.parentElement.appendChild(new Element("a", "", "Download langsmith-0.15.1.tgz"));
  download.href = "https://github.com/langchain-ai/helm/releases/download/langsmith-0.15.1/langsmith-0.15.1.tgz";
  const patchChildren = [...patch.parentElement.children];
  const hidden = dom.heading("langsmith-0-14-0");
  hidden.visible = false;
  dom.flush();
  assert.deepEqual(dom.links().map((link) => [link.href, link.textContent]), [
    ["#langsmith-0-16-0", "langsmith-0.16.0"], ["#langsmith-0-15-0", "langsmith-0.15.0"],
  ]);
  chapters.forEach((heading) => assert.ok(heading.classList.contains("changelog-chapter-heading")));
  [...excluded, hidden].forEach((heading) => assert.equal(heading.className, ""));
  assert.equal(dom.document.getElementById("changelog-chapters-inline").parentElement, dom.content);
  assert.equal(dom.content.firstChild.id, "changelog-chapters-inline");
  chapters.forEach((heading) => {
    assert.equal(heading.parentElement.parentElement.parentElement, dom.content);
    assert.deepEqual(heading.parentElement.children, [heading]);
  });
  assert.deepEqual(patch.parentElement.children, patchChildren);
  assert.equal(patch.textContent, "\u200blangsmith-0.15.1");
  assert.equal(download.textContent, "Download langsmith-0.15.1.tgz");
  assert.equal(download.href, "https://github.com/langchain-ai/helm/releases/download/langsmith-0.15.1/langsmith-0.15.1.tgz");
});

test("other pages do not gain an index or modify ordinary headings", () => {
  const dom = setup({ path: "/langsmith/agent-server-changelog" });
  const headings = [dom.heading("langsmith-0-15-0"), dom.heading("v0-15")];
  dom.flush();
  dom.notify();
  dom.flush();
  headings.forEach((heading) => assert.equal(heading.className, ""));
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 0);
});

test("observer updates coalesce and do not rebuild unchanged indexes", () => {
  const dom = setup();
  dom.heading("langsmith-0-15-0");
  dom.flush();
  const nav = dom.document.getElementById("changelog-chapters-sidebar");
  const originalLink = dom.links()[0];
  dom.notify();
  dom.notify();
  assert.equal(dom.frames.length, 1);
  dom.flush();
  assert.equal(nav.replacements, 1);
  assert.equal(dom.links()[0], originalLink);
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 2);
});

test("leaving cleans up indexes and heading classes; reentering enhances again", () => {
  const dom = setup();
  const heading = dom.heading("langsmith-0-15-0");
  dom.flush();
  dom.root.dataset.currentPath = "/langsmith/overview";
  dom.notify();
  dom.flush();
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 0);
  assert.equal(heading.className, "");
  dom.root.dataset.currentPath = PAGE;
  dom.notify();
  dom.flush();
  assert.equal(dom.links()[0].href, "#langsmith-0-15-0");
  assert.ok(heading.classList.contains("changelog-chapter-heading"));
});

test("filter rerenders remove and rebuild indexes from visible stable launches", () => {
  const dom = setup();
  const chapters = [dom.heading("langsmith-0-16-0"), dom.heading("langsmith-0-15-0")];
  const preview = dom.heading("langsmith-0-17-0-rc-1");
  preview.visible = false;
  dom.flush();
  assert.equal(dom.links().length, 2);
  const originalNav = dom.document.getElementById("changelog-chapters-sidebar");
  chapters.forEach((heading) => { heading.visible = false; });
  preview.visible = true;
  dom.notify();
  dom.flush();
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 0);
  chapters[1].visible = true;
  dom.notify();
  dom.flush();
  assert.notEqual(dom.document.getElementById("changelog-chapters-sidebar"), originalNav);
  assert.deepEqual(dom.links().map((link) => link.href), ["#langsmith-0-15-0"]);
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 2);
  assert.equal(preview.className, "");
});

test("late chapters use the inline fallback without a sidebar and update on insertion", () => {
  const dom = setup({ side: false, loading: true });
  assert.equal(dom.frames.length, 0);
  dom.ready();
  dom.flush();
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 0);
  dom.heading("langsmith-0-16-0");
  dom.notify();
  dom.flush();
  const nav = dom.document.getElementById("changelog-chapters-inline");
  assert.ok(nav.classList.contains("changelog-chapter-index-fallback"));
  assert.equal(nav.attributes["aria-label"], "Minor releases");
  assert.equal(nav.firstChild.textContent, "Minor releases");
  dom.heading("langsmith-0-15-0");
  dom.notify();
  dom.flush();
  assert.deepEqual(dom.links(nav.id).map((link) => link.href), ["#langsmith-0-16-0", "#langsmith-0-15-0"]);
  assert.equal(dom.document.querySelectorAll(".changelog-chapter-index").length, 1);
  assert.equal(nav.replacements, 2);
});
