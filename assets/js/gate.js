/* DEPRECATED — DO NOT USE.
 *
 * This file used to contain a SHA-256 client-side "gate" that was
 * NOT a real access control. Removed for the future subscription
 * system; if you need to gate content, do it in a Worker that checks
 * a server-validated session, not in JavaScript that runs in the
 * user's browser.
 *
 * See audit S-CRIT-01 (May 2026).
 */
