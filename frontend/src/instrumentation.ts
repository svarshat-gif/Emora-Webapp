// Node.js 22+ includes an experimental localStorage global that is NOT
// the browser's Web Storage API. It requires --localstorage-file to work
// properly. Without it, calling localStorage.getItem() throws:
//   TypeError: localStorage.getItem is not a function
//
// This instrumentation file removes the broken global so that libraries
// using `typeof localStorage !== 'undefined'` checks won't mistakenly
// try to use it on the server.
export async function register() {
  if (typeof window === "undefined") {
    // We're on the server — delete the broken Node.js localStorage global
    // so it doesn't interfere with SSR.
    if (typeof globalThis.localStorage !== "undefined") {
      // @ts-expect-error Intentionally removing broken Node.js localStorage
      delete globalThis.localStorage;
    }
  }
}
