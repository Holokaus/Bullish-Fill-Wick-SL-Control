"""Unit tests for src/lib/sim.py replay() — 5 hand-checked cases (directive s8.3).

Each case uses a synthetic series long enough that the replay horizon (TMAX=48) lands on a
real, known bar. Convention: O,Hh,L,C length-N (N>=50); sidx = signal bar, eb = entry bar.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import numpy as np
import lib.sim as S

def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol

def base(N=60):
    O=np.full(N,0.0); O[1]=100.0
    Hh=np.full(N,100.0)          # never reaches TP=120 unless we set it
    L =np.full(N,100.0)
    C =np.full(N,100.0)
    return O,Hh,L,C

def test_a_fill_bar1():
    O,Hh,L,C=base()
    Hh[1]=110.0                   # entry bar1 high hits TP=110
    bt=np.array([100.]); tp=np.array([110.])
    pnl,filled=S.replay(O,Hh,L,C,np.array([0]),np.array([1]),bt,tp,K=0)
    assert filled[0] == True
    assert approx(pnl[0], 1000.0), pnl[0]    # +10% = 1000 bps

def test_b_fill_bar3_with_adverse_bar2():
    O,Hh,L,C=base()
    Hh[3]=120.0                   # TP touched on bar3
    L[2]=90.0; C[2]=95.0          # bar2 dips adverse (-10%), no price stop
    bt=np.array([100.]); tp=np.array([120.])
    pnl,filled=S.replay(O,Hh,L,C,np.array([0]),np.array([1]),bt,tp,K=0)
    assert filled[0] == True
    assert approx(pnl[0], 2000.0), pnl[0]     # +20% = 2000 bps

def test_c_never_fills_horizon_close():
    O,Hh,L,C=base()
    C[48]=95.0                    # horizon close (bar 1+47) = 95
    bt=np.array([100.]); tp=np.array([120.])
    pnl,filled=S.replay(O,Hh,L,C,np.array([0]),np.array([1]),bt,tp,K=0)
    assert filled[0] == False
    assert approx(pnl[0], -500.0), pnl[0]      # (95-100)/100*1e4 = -500 bps

def test_d_time_stop_exits_at_K():
    O,Hh,L,C=base()
    C[3]=80.0                     # close of forward bar K=2 (=idx 3) = 80 (TP never hit)
    bt=np.array([100.]); tp=np.array([120.])
    pnl,filled=S.replay(O,Hh,L,C,np.array([0]),np.array([1]),bt,tp,K=2)
    assert filled[0] == False
    assert approx(pnl[0], -2000.0), pnl[0]     # (80-100)/100*1e4 = -2000 bps

def test_e_tp_and_k_same_bar():
    O,Hh,L,C=base()
    Hh[3]=120.0; C[3]=120.0       # forward bar K=2 (=idx 3) high hits TP
    bt=np.array([100.]); tp=np.array([120.])
    pnl,filled=S.replay(O,Hh,L,C,np.array([0]),np.array([1]),bt,tp,K=2)
    assert filled[0] == True
    assert approx(pnl[0], 2000.0), pnl[0]      # +20% = 2000 bps

if __name__ == "__main__":
    for f in (test_a_fill_bar1, test_b_fill_bar3_with_adverse_bar2,
              test_c_never_fills_horizon_close, test_d_time_stop_exits_at_K,
              test_e_tp_and_k_same_bar):
        f()
        print("PASS", f.__name__)
    print("ALL 5 CASES PASS")
