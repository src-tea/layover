export function calculateUsableLayover(layoverMinutes, airportExitMinutes = 15, returnTravelMinutes = 20, returnBuffer = 30) {
  if (!Number.isFinite(layoverMinutes)) return 0;
  return Math.max(0, layoverMinutes - airportExitMinutes - returnTravelMinutes - returnBuffer);
}
