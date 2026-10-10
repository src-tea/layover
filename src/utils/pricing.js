import { fromMinorUnits, toMinorUnits } from './currency';

function divideRounded(totalMinorUnits, divisor) {
  const total = BigInt(totalMinorUnits);
  const count = BigInt(divisor);
  const magnitude = total < 0n ? -total : total;
  const rounded = (magnitude + count / 2n) / count;
  return Number(total < 0n ? -rounded : rounded);
}

export function calculateSharedCost({ totalPrice = 0, eligibleParticipants = 1, soloPrice = 0, platformFee = 0 }) {
  const totalMinorUnits = toMinorUnits(totalPrice || 0);
  const soloMinorUnits = toMinorUnits(soloPrice || totalPrice || 0);
  const eligibleCount = Math.max(1, Math.floor(Number(eligibleParticipants || 1)));
  const feeMinorUnits = toMinorUnits(platformFee || 0);
  const perParticipantMinorUnits = divideRounded(totalMinorUnits, eligibleCount);
  const finalMinorUnits = perParticipantMinorUnits + feeMinorUnits;
  const savingsMinorUnits = soloMinorUnits - finalMinorUnits;

  return {
    total: fromMinorUnits(totalMinorUnits),
    perParticipant: fromMinorUnits(perParticipantMinorUnits),
    savings: fromMinorUnits(savingsMinorUnits),
    eligibleCount,
    fee: fromMinorUnits(feeMinorUnits),
    finalTotal: fromMinorUnits(finalMinorUnits),
    platformFee: fromMinorUnits(feeMinorUnits),
  };
}
