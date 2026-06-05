async function submitComplaint() {
  let text = document.getElementById("complaint").value.trim();

  // Fix: validate input before sending
  if (!text) {
    document.getElementById("result").innerHTML = "<span style='color:red'>Please enter a complaint.</span>";
    return;
  }

  try {
    let response = await fetch("http://127.0.0.1:5000/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ complaint: text })
    });

    // Fix: handle HTTP errors
    if (!response.ok) {
      let err = await response.json();
      document.getElementById("result").innerHTML = "<span style='color:red'>Error: " + (err.error || "Unknown error") + "</span>";
      return;
    }

    let data = await response.json();
    document.getElementById("result").innerHTML =
      "<b>Category:</b> " + data.category +
      "<br><b>Priority:</b> " + data.priority;

    document.getElementById("complaint").value = "";
  } catch (e) {
    document.getElementById("result").innerHTML = "<span style='color:red'>Could not connect to server. Is Flask running?</span>";
  }
}

async function viewClusters() {
  try {
    let response = await fetch("http://127.0.0.1:5000/clusters");

    if (!response.ok) {
      let err = await response.json();
      document.getElementById("clusters").innerHTML = "<span style='color:red'>" + (err.error || "Error fetching clusters") + "</span>";
      return;
    }

    let data = await response.json();
    let html = "<ul>";
    data.forEach(item => {
      html += `<li><b>Cluster ${item.cluster}:</b> ${item.complaint}</li>`;
    });
    html += "</ul>";
    document.getElementById("clusters").innerHTML = html;
  } catch (e) {
    document.getElementById("clusters").innerHTML = "<span style='color:red'>Could not connect to server.</span>";
  }
}
