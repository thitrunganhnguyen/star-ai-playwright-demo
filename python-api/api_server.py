import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from ai_agent import generate_test_steps


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8931/mcp")

app = Flask(__name__)
CORS(app)


async def execute_steps_via_mcp(steps):
    results = []

    async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            for step in steps:
                action = step.get("action")

                if action == "goto":
                    await session.call_tool(
                        "browser_navigate",
                        {"url": step["url"]}
                    )
                    results.append(f"Navigated to {step['url']}")

                elif action == "fill":
                    await session.call_tool(
                        "browser_type",
                        {
                            "target": step["selector"],
                            "text": step["value"]
                        }
                    )
                    results.append(f"Filled {step['selector']}")

                elif action == "click":
                    await session.call_tool(
                        "browser_click",
                        {"target": step["selector"]}
                    )
                    results.append(f"Clicked {step['selector']}")

                elif action == "expectText":
                    await session.call_tool(
                        "browser_wait_for",
                        {"text": step["value"]}
                    )
                    results.append(f"Verified text {step['value']}")

                elif action == "screenshot":
                    screenshot_name = step.get("name") or step.get("path") or "screenshot"
                    screenshot_name = screenshot_name.replace(".png", "")

                    await session.call_tool(
                        "browser_take_screenshot",
                        {
                            "type": "png",
                            "filename": f"test-results/{screenshot_name}.png",
                            "fullPage": True
                        }
                    )
                    results.append(f"Screenshot saved: {screenshot_name}.png")

                else:
                    results.append(f"Unsupported action: {action}")

    return {
        "status": "passed",
        "results": results
    }


@app.route("/api/ai-test", methods=["POST"])
def ai_test():
    try:
        data = request.get_json()
        goal = data.get("goal") if data else None

        if not goal:
            return jsonify({"error": "goal is required"}), 400

        steps = generate_test_steps(goal)
        execution_result = asyncio.run(execute_steps_via_mcp(steps))

        return jsonify({
            "goal": goal,
            "generatedSteps": steps,
            "executionResult": execution_result
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mcpServerUrl": MCP_SERVER_URL
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)