# Design explanation

## Immediate safety thresholds
This prototype uses illustrative hard limits of 85 N·m joint torque, 90 °C joint temperature, and 18 mm/s vibration. Any one joint crossing any one limit triggers `EMERGENCY_STOP` before the predictive model is consulted. These values are not manufacturer-approved limits; real installations require validated robot-specific limits, safety-rated hardware, and risk assessment. Invalid or negative readings are also treated as unsafe.

## Predictive wear and maintenance notes
A Random Forest classifier is trained on 120 synthetic historical readings with binary wear labels. It estimates wear risk from torque, temperature, and vibration. Technician notes are scanned independently for transparent high- and medium-risk phrases. A high-risk note or predicted wear probability of at least 0.75 schedules maintenance; a medium-risk note or probability of at least 0.40 requests monitoring. The immediate hard-limit check always has priority and does not depend on ML availability or correctness.

## Spoofed-sensor defense
The prototype flags non-finite/negative values, a suspicious combination of high vibration and temperature with implausibly low torque, and a sudden torque drop compared with a previous sample while vibration remains elevated. A detected inconsistency leads to `SCHEDULE_MAINTENANCE` unless the hard safety check already requires `EMERGENCY_STOP`. This can catch simple inconsistent readings but cannot guarantee detection of coordinated attacks, replayed plausible values, or a compromised acquisition system. Production systems should add authenticated sensor communications, secure timestamps, redundant sensing, audit logs, and independent safety interlocks.

## Four decision examples
Run `python main.py`. It prints explicit examples for `SAFE`, `MONITOR`, `SCHEDULE_MAINTENANCE`, and `EMERGENCY_STOP`, followed by a sample fleet report. The examples use fixed notes so all four outcomes can be demonstrated independently of model probability.

## Limitations
The dataset is synthetic, the text analysis uses transparent keywords rather than a language model, and the classifier score is not evidence of real-world predictive performance. The implementation is an educational prototype, not a certified industrial safety controller.
