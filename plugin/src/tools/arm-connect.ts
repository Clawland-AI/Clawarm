import { BridgeClient } from "../bridge-client.js";

export function registerArmConnect(api: any, client: BridgeClient, defaultRobot: string) {
  api.registerTool({
    name: "arm_connect",
    description:
      "Connect to a robotic arm (NERO 7-DOF or Piper 6-DOF) via the ClawArm bridge. " +
      "The arm will be enabled and ready for motion commands after connection.",
    parameters: {
      type: "object",
      properties: {
        robot: {
          type: "string",
          enum: ["nero", "piper", "piper_h", "piper_l", "piper_x"],
          description: "Robot type to connect to",
          default: defaultRobot,
        },
        channel: {
          type: "string",
          description: "CAN interface name",
          default: "can0",
        },
      },
    },
    async execute({ robot, channel }: { robot?: string; channel?: string }) {
      try {
        const result = await client.connect(
          robot || defaultRobot,
          channel || "can0"
        );
        return {
          content: [{ type: "text", text: JSON.stringify(result) }],
        };
      } catch (err: any) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ error: err.message }),
              advice: "Check that the bridge server is running (clawarm-bridge) and CAN is activated",
            },
          ],
        };
      }
    },
  });
}
