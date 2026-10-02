import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import ccxt
from config.settings import (
    GROQ_API_KEY,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    SUPABASE_URL,
    SUPABASE_KEY,
    EXCHANGE_ID,
    SYMBOL
)
from tools.market_data import get_exchange_instance

def run_health_checks() -> bool:
    """
    Performs comprehensive diagnostic checks across all external dependencies,
    credentials, filesystem permissions, and connectivity.
    """
    print("\n" + "=" * 60)
    print("[*] AI TRADING FIRM: PRODUCTION HEALTH & READINESS CHECK")
    print("=" * 60)

    all_critical_passed = True

    # 1. Environment & Secrets Check
    print("\n[1] Environment & API Secrets:")
    if GROQ_API_KEY and len(GROQ_API_KEY.strip()) > 10:
        print(f"  ✅ GROQ_API_KEY: Configured (Length: {len(GROQ_API_KEY)})")
    else:
        print("  ❌ GROQ_API_KEY: MISSING or INVALID (Required for AI Agents)")
        all_critical_passed = False

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        print("  ✅ TELEGRAM: Configured (Bot Token & Chat ID present)")
    else:
        print("  ⚠️ TELEGRAM: Not configured (Optional: live mobile alerts disabled)")

    if SUPABASE_URL and SUPABASE_KEY:
        print("  ✅ SUPABASE: Configured (URL & Key present)")
    else:
        print("  ⚠️ SUPABASE: Not configured (Optional: web dashboard persistence disabled)")

    # 2. Exchange Connectivity Check
    print(f"\n[2] Exchange Public Connectivity ({EXCHANGE_ID.upper()}):")
    try:
        exchange = get_exchange_instance()
        # Fetch public market status or ticker without placing orders
        ticker = exchange.fetch_ticker(SYMBOL)
        last_price = ticker.get('last') or ticker.get('close')
        print(f"  ✅ Exchange API Connected successfully! Last {SYMBOL} price: {last_price}")
    except Exception as e:
        print(f"  ❌ Exchange Connection Failed: {str(e)}")
        all_critical_passed = False

    # 3. Filesystem & Logging Permissions Check
    print("\n[3] Filesystem & Log Storage:")
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        test_file = os.path.join(log_dir, ".health_check_test")
        with open(test_file, "w") as f:
            f.write("health_check_ok")
        os.remove(test_file)
        print("  ✅ Filesystem read/write verified (logs/ directory writable)")
    except Exception as e:
        print(f"  ❌ Filesystem check failed: {str(e)}")
        all_critical_passed = False

    print("\n" + "=" * 60)
    if all_critical_passed:
        print("🟢 OVERALL STATUS: SYSTEM READY FOR EXECUTION")
    else:
        print("🔴 OVERALL STATUS: HEALTH CHECK FAILED (Resolve issues above)")
    print("=" * 60 + "\n")

    return all_critical_passed

if __name__ == "__main__":
    success = run_health_checks()
    sys.exit(0 if success else 1)
