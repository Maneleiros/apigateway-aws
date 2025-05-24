fetch("https://4i14s9gix5.execute-api.us-east-1.amazonaws.com/prod/stations")
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById("stations");
    data.forEach(station => {
      const item = document.createElement("li");
      item.textContent = station.AddressInfo.Title + " - " + station.AddressInfo.Town;
      list.appendChild(item);
    });
  });
