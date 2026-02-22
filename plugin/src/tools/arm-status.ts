import { BridgeClient } from "../bridge-client.js";

export function registerArmStatus(api: any, client: BridgeClient) {
  api.registerTool({
    name: "arm_status",
    description:
      "Get the current status of the connected robotic arm: joint angles (radians), " +
      "flange pose (meters/radians), motion status (0=idle), and connection state.",
    parameters: {
      type: "object",
      properties: {},
    },
    async execute() {
      try {
        const status = await client.getStatus();
        return {
          content: [{ type: "text", text: JSON.stringify(status, null, 2) }],
        };
      } catch (err: any) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ error: err.message }),
              advice: "Check that the bridge server is running",
            },
          ],
        };
      }
    },
  });
}
