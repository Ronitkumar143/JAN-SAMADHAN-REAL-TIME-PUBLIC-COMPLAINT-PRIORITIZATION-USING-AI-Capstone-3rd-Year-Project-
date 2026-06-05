async function submitComplaint() {
  let text = document.getElementById("complaint").value.trim();

  if (!text) {
    document.getElementById("result").innerHTML =
      "<span style='color:red'>Please enter a complaint.</span>";
    return;
  }

  try {
    let response = await fetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ complaint: text })
    });

    let data = await response.json();

    document.getElementById("result").innerHTML =
      "<b>Predicted Category:</b> " + data.category;

    document.getElementById("complaint").value = "";

  } catch (e) {
    document.getElementById("result").innerHTML =
      "<span style='color:red'>Could not connect to server.</span>";
  }
}
