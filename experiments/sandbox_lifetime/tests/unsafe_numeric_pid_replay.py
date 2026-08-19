"""Expected-failure seed: numeric PID + old launch receipt is treated as authority."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Receipt:
    pid: int
    launch_ok: bool

def unsafe_accept(receipt: Receipt, observed_pid: int) -> bool:
    return receipt.launch_ok and receipt.pid == observed_pid

def main() -> None:
    old = Receipt(pid=4242, launch_ok=True)
    reused_numeric_pid = 4242
    assert not unsafe_accept(old, reused_numeric_pid), "unsafe design replayed stale authority"

if __name__ == "__main__":
    main()
