import { BridgeClient } from "./src/bridge-client.js";
import { registerArmConnect } from "./src/tools/arm-connect.js";
import { registerArmMove } from "./src/tools/arm-move.js";
import { registerArmStatus } from "./src/tools/arm-status.js";
import { registerArmStop } from "./src/tools/arm-stop.js";

export default {
  id: "clawarm",
  name: "ClawArm",

  register(api: any) {
    const bridgeUrl: string = api.config?.bridgeUrl || "http://localhost:8420";
    const defaultRobot: string = api.config?.defaultRobot || "nero";

    const client = new BridgeClient(bridgeUrl);

    registerArmConnect(api, client, defaultRobot);
    registerArmStatus(api, client);
    registerArmMove(api, client);
    registerArmStop(api, client);
  },
};
