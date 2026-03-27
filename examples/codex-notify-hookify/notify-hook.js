#!/usr/bin/env node

require("coffee-script/register");

const fs = require("node:fs");
const path = require("node:path");
const Hookify = require("hookify");

class CodexNotifyPipeline extends Hookify {
  handle(payload, done) {
    this.runPre(payload.type, [payload], (preErr) => {
      if (preErr) {
        return done(preErr);
      }

      const outputDir = path.join(__dirname, "output");
      const logPath = path.join(outputDir, "notify.log");

      fs.mkdirSync(outputDir, { recursive: true });
      fs.appendFileSync(
        logPath,
        `${JSON.stringify(
          {
            type: payload.type,
            threadId: payload["thread-id"],
            turnId: payload["turn-id"],
            cwd: payload.cwd,
            client: payload.client ?? null,
            inputMessages: payload["input-messages"] ?? [],
            lastAssistantMessage: payload["last-assistant-message"] ?? null,
            handledAt: new Date().toISOString()
          },
          null,
          0
        )}\n`,
        "utf8"
      );

      this.runPost(payload.type, [payload], done);
    });
  }
}

function readPayload() {
  const raw = process.argv[process.argv.length - 1];

  if (!raw) {
    throw new Error("Expected Codex notify JSON payload as the final argv item.");
  }

  const payload = JSON.parse(raw);

  if (payload.type !== "agent-turn-complete") {
    throw new Error(`Unsupported notify payload type: ${payload.type}`);
  }

  return payload;
}

const pipeline = new CodexNotifyPipeline();

pipeline.pre("agent-turn-complete", (payload, next) => {
  payload.receivedAt = new Date().toISOString();
  next();
});

pipeline.post("agent-turn-complete", (payload, next) => {
  const summaryPath = path.join(__dirname, "output", "last-summary.txt");
  const summary = [
    `type=${payload.type}`,
    `thread_id=${payload["thread-id"]}`,
    `turn_id=${payload["turn-id"]}`,
    `client=${payload.client ?? "unknown"}`,
    `cwd=${payload.cwd}`,
    `last_assistant_message=${payload["last-assistant-message"] ?? ""}`
  ].join("\n");

  fs.writeFileSync(summaryPath, `${summary}\n`, "utf8");
  next();
});

try {
  const payload = readPayload();
  pipeline.handle(payload, (err) => {
    if (err) {
      process.stderr.write(`${err.message}\n`);
      process.exitCode = 1;
    }
  });
} catch (err) {
  process.stderr.write(`${err.message}\n`);
  process.exit(1);
}
