async function loadData() {
  const response = await fetch('../data/latest.json');
  const data = await response.json();
  // TODO: Render map and leaderboard
}
loadData();
