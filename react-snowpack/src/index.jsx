import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App.jsx";

const root = createRoot(document.getElementById("root"));
root.render(<App />);

// Hot Module Replacement (HMR) - Remove this snippet to remove HMR.
// Learn more: https://www.snowpack.dev/concepts/hot-module-replacement
if (undefined /* [snowpack] import.meta.hot */) {
  undefined /* [snowpack] import.meta.hot */
    .accept();
}
