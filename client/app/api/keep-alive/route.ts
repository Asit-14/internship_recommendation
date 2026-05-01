import { NextResponse } from "next/server";

export async function GET() {
  try {
    const apiBaseUrl =
      process.env.API_BASE_URL ||
      "https://internship-recommendation-gypb.onrender.com/api/v1";

    // Remove "/api/v1" safely (only if it's at the end)
    const baseUrl = apiBaseUrl.endsWith("/api/v1")
      ? apiBaseUrl.slice(0, -7)
      : apiBaseUrl;

    const healthUrl = `${baseUrl}/health`;

    // Add timeout (important for serverless)
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(healthUrl, {
      method: "GET",
      cache: "no-store",
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          message: `Ping failed with status ${response.status}`,
        },
        { status: response.status },
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: "Keep-alive ping successful",
      data,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Unknown error";

    return NextResponse.json(
      {
        success: false,
        message: "Keep-alive ping failed",
        error: message,
      },
      { status: 500 },
    );
  }
}
