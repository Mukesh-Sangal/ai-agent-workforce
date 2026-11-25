const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "127.0.0.1:8000").replace(/\/+$/, "");

export async function analyzeTask(description) {
	const controller = new AbortController()
	const timeout = setTimeout(() => controller.abort(), 45000);

	try {
		const response = await fetch(`${API_BASE_URL}/task-analyses`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ description }),
			signal: controller.signal
		})

		const data = await response.json().catch(() => null);
		if (!response.ok) {
			const detail = data?.detail

			const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map(item => item.msg).filter(Boolean).join(" ") : "";

			throw new Error(message || `Analyses failed (HTTP ${response.status})`)
		}
		if (!data || typeof data.goal !== "string" || typeof data.expected_deliverable !== "string" ||
			!Array.isArray(data.missing_information || !data.missing_information.every((item) => typeof item === "string"))
		) {
			throw new Error("The Service returned an unexpected analysis format.")
		}
		return data
	} catch (error) {
		if (error.name === "AbortError") {
			throw new Error(
				"Theanalysis request timed out. Please try again later"
			);
		}
		if (error instanceof TypeError) {
			throw new Error(
				"Cannot reach the analysis service. Check that the backend is running"
			);
		}
		throw error
	} finally {
		clearTimeout(timeout)
	}

}