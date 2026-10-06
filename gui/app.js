"use strict";

const SLIPS_PER_LANE = 4;
const ROUTE_NAMES = { escalate: "Escalate", code: "Code", faq: "FAQ", answer: "Answer", refuse: "Refuse" };

/** Build an element. All text goes in via textContent, never innerHTML. */
function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    node.append(...children.filter((child) => child !== null && child !== undefined));
    return node;
}

async function api(url, options) {
    const response = await fetch(url, options);
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `The request failed (${response.status}).`);
    return body;
}

function routePill(route) {
    return el("span", { class: `pill r-${route}` }, ROUTE_NAMES[route] || route);
}

// --- Tabs -------------------------------------------------------------------

const tabs = [...document.querySelectorAll('[role="tab"]')];

function selectTab(tab) {
    for (const t of tabs) {
        const selected = t === tab;
        t.setAttribute("aria-selected", String(selected));
        t.tabIndex = selected ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
    }
    if (tab.id === "tab-results" && !resultsData) loadResults();
}

tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
        const step = event.key === "ArrowRight" ? 1 : tabs.length - 1;
        const next = tabs[(i + step) % tabs.length];
        next.focus();
        selectTab(next);
    });
});

// --- Try a message ------------------------------------------------------------

const form = document.getElementById("route-form");
const textarea = document.getElementById("message");
const submitButton = form.querySelector('button[type="submit"]');
const routeError = document.getElementById("route-error");

async function routeMessage(message) {
    routeError.hidden = true;
    submitButton.disabled = true;
    try {
        const result = await api("?action=route", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        dropSlip(message, result);
    } catch (error) {
        routeError.textContent = error.message;
        routeError.hidden = false;
    } finally {
        submitButton.disabled = false;
    }
}

function dropSlip(message, result) {
    const lane = document.querySelector(`.lane[data-route="${result.route}"]`);
    if (!lane) throw new Error(`The router returned an unknown route: ${result.route}`);

    document.querySelectorAll(".is-hit, .is-new").forEach((node) => node.classList.remove("is-hit", "is-new"));

    const slips = lane.querySelector(".slips");
    slips.prepend(el("li", { class: "slip is-new" }, el("q", {}, message), result.reason));
    while (slips.children.length > SLIPS_PER_LANE) slips.lastElementChild.remove();

    const count = lane.querySelector(".count");
    count.textContent = String(Number(count.textContent) + 1);
    lane.classList.add("is-hit");

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    lane.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = textarea.value.trim();
    if (message) routeMessage(message);
});

// Enter routes the message; Shift+Enter adds a new line.
textarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        form.requestSubmit();
    }
});

document.querySelectorAll(".example").forEach((button) => {
    button.addEventListener("click", () => {
        textarea.value = button.dataset.message;
        routeMessage(button.dataset.message);
    });
});

// --- Test results -------------------------------------------------------------

const resultsBox = document.getElementById("results");
const resultsStatus = document.getElementById("results-status");
const onlyWrong = document.getElementById("only-wrong");
let resultsData = null;

async function loadResults() {
    resultsStatus.textContent = "Running the tests…";
    resultsStatus.hidden = false;
    resultsBox.replaceChildren();
    try {
        resultsData = await api("?action=evaluate");
        renderResults();
        resultsStatus.hidden = true;
    } catch (error) {
        resultsData = null;
        resultsStatus.textContent = `Could not run the tests. ${error.message}`;
    }
}

function renderResults() {
    resultsBox.replaceChildren(
        renderSet("Provided test set", "The 20 messages from the brief, labels unchanged.", resultsData.provided),
        renderSet("Additional cases", "Messages we wrote to probe the rules, including known gaps.", resultsData.extra),
    );
}

function metric(label, value, bad) {
    return el("div", bad ? { class: "bad" } : {}, el("dt", {}, label), el("dd", {}, value));
}

function renderSet(title, description, summary) {
    const missed = summary.urgent_total - summary.urgent_caught;
    const accuracy = Math.round((100 * summary.correct) / summary.total);

    const rows = summary.rows.filter((row) => !onlyWrong.checked || !row.correct);
    const body = el("tbody");
    for (const row of rows) {
        body.append(el("tr", row.correct ? {} : { class: "wrong" },
            el("td", {}, row.id),
            el("td", { class: "msg" }, row.message),
            el("td", {}, routePill(row.expected)),
            el("td", {}, routePill(row.got)),
            el("td", { class: "why" }, row.reason),
        ));
        if (!row.correct && row.dispute) {
            body.append(noteRow("Label disputed:", ` we propose ${ROUTE_NAMES[row.dispute.proposed_route]}. ${row.dispute.why}`));
        }
        if (!row.correct && row.known_gap) {
            body.append(noteRow("Known gap:", ` ${row.known_gap}`));
        }
    }
    if (!rows.length) body.append(el("tr", {}, el("td", { colspan: "5" }, "No wrong rows.")));

    return el("section", { class: "set" },
        el("h2", {}, title),
        el("p", { class: "aside" }, description),
        missed > 0
            ? el("p", { class: "alert" }, `${missed} urgent message${missed > 1 ? "s" : ""} missed. These patients would not reach the care team.`)
            : null,
        el("dl", { class: "metrics" },
            metric("Urgent messages caught", `${summary.urgent_caught} of ${summary.urgent_total}`, missed > 0),
            metric("Non-urgent wrongly escalated", `${summary.false_escalations} of ${summary.non_urgent_total}`, false),
            metric("Overall accuracy", `${summary.correct} of ${summary.total} (${accuracy}%)`, false),
        ),
        summary.correct_with_disputes === null
            ? null
            : el("p", { class: "aside" }, `With our disputed labels corrected: ${summary.correct_with_disputes} of ${summary.total}.`),
        el("div", { class: "table-scroll" },
            el("table", {},
                el("thead", {}, el("tr", {}, ...["#", "Message", "Expected", "Got", "Reason"].map((h) => el("th", { scope: "col" }, h)))),
                body,
            ),
        ),
    );
}

function noteRow(label, text) {
    return el("tr", { class: "note" }, el("td", {}), el("td", { colspan: "4" }, el("strong", {}, label), text));
}

onlyWrong.addEventListener("change", () => resultsData && renderResults());
document.getElementById("rerun").addEventListener("click", loadResults);
