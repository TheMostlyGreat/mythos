import * as compiler from "@astrojs/compiler";

import { runAsWorker } from "synckit";

runAsWorker((method, ...args) => compiler[method](...args));
