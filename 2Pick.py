import streamlit as st
import random
from collections import Counter
from datetime import datetime

# サンプルカードデッキ（必要に応じて画像URLや追加フィールドを入れて拡張してください）
DECK = [
    {"id": 1, "name": "ドラゴン", "emoji": "🐉"},
    {"id": 2, "name": "フェニックス", "emoji": "🔥"},
    {"id": 3, "name": "ユニコーン", "emoji": "🦄"},
    {"id": 4, "name": "ゴーレム", "emoji": "🪨"},
    {"id": 5, "name": "エルフ", "emoji": "🧝"},
    {"id": 6, "name": "ナイト", "emoji": "🛡️"},
    {"id": 7, "name": "ウィザード", "emoji": "🪄"},
    {"id": 8, "name": "スライム", "emoji": "🟢"},
    {"id": 9, "name": "サムライ", "emoji": "⚔️"},
    {"id": 10, "name": "ロボット", "emoji": "🤖"},
]

# ---------- セッションステートの初期化 ----------
if "collection" not in st.session_state:
    st.session_state.collection = []  # 選んで追加されたカード（カード辞書のコピーを格納）
if "history" not in st.session_state:
    st.session_state.history = []  # 選択履歴（時刻、どちらを選んだか、カード情報）
if "round" not in st.session_state:
    st.session_state.round = 1
if "left_set" not in st.session_state:
    st.session_state.left_set = None
if "right_set" not in st.session_state:
    st.session_state.right_set = None
if "allow_duplicates" not in st.session_state:
    st.session_state.allow_duplicates = True  # 同じカードを何度も追加できるか

# ---------- ヘルパー関数 ----------
def draw_two_sets(deck, allow_duplicates=True):
    """
    デッキからランダムに「2枚ずつのセットを2つ」作成して返す。
    allow_duplicates=False の場合は、4枚すべてが異なるカードになるようにする。
    戻り値: (left_set, right_set) — 各セットはカード辞書のリスト（長さ2）
    """
    if allow_duplicates:
        # 単純にランダムに4枚（重複可）を取り、左右に分ける
        picks = [random.choice(deck) for _ in range(4)]
    else:
        if len(deck) < 4:
            raise ValueError("デッキのカード数が4未満です。重複を許可しない場合はカードを増やしてください。")
        picks = random.sample(deck, 4)
    left = [picks[0], picks[1]]
    right = [picks[2], picks[3]]
    return left, right

def add_set_to_collection(card_set):
    """選択したカードセット（リスト）をコレクションへ追加し、履歴に残す"""
    # コレクションへの追加（カードオブジェクトのコピーを入れておくと安全）
    for c in card_set:
        st.session_state.collection.append(dict(c))
    # 履歴
    st.session_state.history.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "round": st.session_state.round,
        "chosen": [c["id"] for c in card_set],
        "chosen_names": [c["name"] for c in card_set],
    })
    st.session_state.round += 1
    # 次のラウンドで新しいセットを引くために現在のセット情報を消す
    st.session_state.left_set = None
    st.session_state.right_set = None

def render_card(c):
    """カード表示用（emoji と名前）"""
    return f"{c.get('emoji','')}  {c.get('name','(no name)')}"

# ---------- UI ----------
st.title("カードセット選択アプリ")
st.write("ランダムに提示される「2枚セット×2組（左セット／右セット）」のうち、どちらか一方を選んでコレクションに追加していくアプリです。")

# オプション: 重複許可の切り替え
allow_dup = st.checkbox("同じカードを何度でも追加できる（重複許可）", value=st.session_state.allow_duplicates)
st.session_state.allow_duplicates = allow_dup

# 初回または前ラウンドで選択済みなら新しいセットを引く
if st.session_state.left_set is None or st.session_state.right_set is None:
    try:
        left_set, right_set = draw_two_sets(DECK, allow_duplicates=st.session_state.allow_duplicates)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    st.session_state.left_set = left_set
    st.session_state.right_set = right_set

# 表示: 左右のセット
col1, col2 = st.columns(2)
with col1:
    st.subheader("左のセット")
    for c in st.session_state.left_set:
        st.markdown(f"### {render_card(c)}")
    if st.button("左を選ぶ", key=f"choose_left_{st.session_state.round}"):
        add_set_to_collection(st.session_state.left_set)
        st.experimental_rerun()

with col2:
    st.subheader("右のセット")
    for c in st.session_state.right_set:
        st.markdown(f"### {render_card(c)}")
    if st.button("右を選ぶ", key=f"choose_right_{st.session_state.round}"):
        add_set_to_collection(st.session_state.right_set)
        st.experimental_rerun()

# 操作: スキップ（追加せず次へ） / リセット
st.write("---")
ops_col1, ops_col2 = st.columns([1, 3])
with ops_col1:
    if st.button("スキップして次へ"):
        # 追加せずラウンドを進める
        st.session_state.history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "round": st.session_state.round,
            "chosen": None,
            "chosen_names": None,
            "action": "skip",
        })
        st.session_state.round += 1
        st.session_state.left_set = None
        st.session_state.right_set = None
        st.experimental_rerun()

with ops_col2:
    if st.button("コレクションをリセット"):
        st.session_state.collection = []
        st.session_state.history = []
        st.session_state.round = 1
        st.session_state.left_set = None
        st.session_state.right_set = None
        st.success("コレクションと履歴をリセットしました。")
        st.experimental_rerun()

# コレクション表示
st.write("---")
st.subheader("現在のコレクション")
if not st.session_state.collection:
    st.info("まだカードが追加されていません。")
else:
    # 名前で集計して表示（枚数を表示）
    names = [c["name"] for c in st.session_state.collection]
    counts = Counter(names)
    for name, cnt in counts.most_common():
        # emoji を先頭の一致カードから探す
        emoji = next((c["emoji"] for c in st.session_state.collection if c["name"] == name), "")
        st.write(f"{emoji} {name} — {cnt} 枚")

    # 詳細リストを展開表示
    with st.expander("コレクションの全アイテム（時系列）を表示"):
        for i, c in enumerate(st.session_state.collection, start=1):
            st.write(f"{i}. {render_card(c)}")

# 履歴表示
st.subheader("選択履歴")
if not st.session_state.history:
    st.info("まだ履歴がありません。")
else:
    for h in reversed(st.session_state.history[-20:]):  # 最新20件を逆順で
        t = h.get("timestamp", "")
        rnd = h.get("round", "")
        if h.get("action") == "skip":
            st.write(f"[{t}] ラウンド {rnd} — スキップ")
        elif h.get("chosen") is None:
            st.write(f"[{t}] ラウンド {rnd} — 追加なし")
        else:
            names = ", ".join(h.get("chosen_names", []))
            st.write(f"[{t}] ラウンド {rnd} — 追加: {names}")

# 小さな注意書き
st.caption("注意: このアプリはセッションステートに依存します。ブラウザをリロードしたりセッションが切れると状態が初期化されます。")
