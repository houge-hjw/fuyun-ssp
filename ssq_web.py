import streamlit as st
import random
import datetime
import itertools
from ssq_core import (
    fetch_lottery_data, load_cache,
    analyze_frequency, analyze_missing, analyze_hot_cold,
    generate_prediction, generate_wheel, generate_rollover_numbers,
    calc_next_issue, calc_next_draw_date, check_prize,
)

st.set_page_config(
    page_title="🎊 福运双色球 · 必中大奖 🎊",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        background: linear-gradient(180deg, #8B0000 0%, #C1272D 50%, #8B0000 100%) !important;
        color: #FFF8E7 !important;
        font-family: "STKaiti", "KaiTi", "楷体", serif !important;
    }
    .stApp { background: linear-gradient(180deg, #8B0000 0%, #C1272D 50%, #8B0000 100%) !important; }
    h1, h2, h3, h4, h5, h6 { color: #FFD700 !important; font-family: "STKaiti","KaiTi","楷体",serif !important; text-shadow: 0 2px 6px rgba(0,0,0,0.5) !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #DAA520 100%) !important;
        color: #8B0000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        border: 2px solid #FFE4B5 !important;
        box-shadow: 0 4px 15px rgba(255,215,0,0.4) !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,215,0,0.6) !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(139,0,0,0.6) !important;
        color: #FFD700 !important;
        border-radius: 10px 10px 0 0 !important;
        font-size: 16px !important;
        padding: 10px 16px !important;
        border: 1px solid #FFD700 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700 0%, #DAA520 100%) !important;
        color: #8B0000 !important;
        font-weight: bold !important;
    }
    .ball-red {
        display: inline-flex; align-items: center; justify-content: center;
        width: 42px; height: 42px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #FF6B6B, #C1272D 60%, #8B0000);
        color: white; font-weight: bold; font-size: 17px;
        margin: 3px; box-shadow: 0 3px 8px rgba(0,0,0,0.5), inset 0 -3px 6px rgba(0,0,0,0.3);
        text-shadow: 0 1px 2px rgba(0,0,0,0.6);
    }
    .ball-blue {
        display: inline-flex; align-items: center; justify-content: center;
        width: 42px; height: 42px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #5A9BFF, #1E5AA8 60%, #0A2E6B);
        color: white; font-weight: bold; font-size: 17px;
        margin: 3px; box-shadow: 0 3px 8px rgba(0,0,0,0.5), inset 0 -3px 6px rgba(0,0,0,0.3);
        text-shadow: 0 1px 2px rgba(0,0,0,0.6);
    }
    .row-card {
        background: rgba(255,248,231,0.1) !important;
        border: 1px solid #FFD700 !important;
        border-radius: 15px !important;
        padding: 10px 15px !important;
        margin: 8px 0 !important;
        backdrop-filter: blur(5px) !important;
    }
    .issue-badge {
        display: inline-block; background: linear-gradient(135deg,#FFD700,#DAA520);
        color: #8B0000; font-weight: bold; border-radius: 20px;
        padding: 4px 14px; margin-right: 10px;
    }
    .copy-btn {
        display: inline-block; background: linear-gradient(135deg,#FFD700,#DAA520);
        color: #8B0000; font-weight: bold; border-radius: 8px;
        padding: 4px 12px; cursor: pointer; border: 1px solid #FFE4B5;
        font-size: 13px; text-decoration: none; margin-left: 8px;
    }
    .strategy-tag {
        color: #FFD700; font-size: 14px; font-weight: bold; margin-right: 8px;
    }
    .footer-tip {
        text-align: center; color: #FFD700; font-size: 14px;
        padding: 20px 10px; opacity: 0.9;
    }
    .title-main {
        text-align: center; padding: 15px 10px;
    }
    .title-main h1 {
        font-size: clamp(22px, 6vw, 42px) !important;
    }
    .title-sub {
        text-align: center; color: #FFE4B5; font-size: 14px; margin-bottom: 15px;
    }
    @media (max-width: 600px) {
        .ball-red, .ball-blue { width: 34px; height: 34px; font-size: 14px; margin: 2px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<div class="title-main">
    <h1>🏆 福运双色球 · 必中大奖 🏆</h1>
</div>
<div class="title-sub">
    🎉 恭喜发财 · 好运连连 · 心想事成 🎉
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch(count):
    data = fetch_lottery_data(count)
    return data


def render_red_balls(red_list):
    balls = "".join(f'<span class="ball-red">{n:02d}</span>' for n in red_list)
    return balls


def render_blue_ball(blue_num):
    return f'<span class="ball-blue">{blue_num:02d}</span>'


def render_row(red_list, blue_num, prefix="", suffix_html=""):
    return f'{prefix}{render_red_balls(red_list)} <span style="color:#FFD700;font-size:20px;margin:0 5px;">+</span> {render_blue_ball(blue_num)}{suffix_html}'


st.markdown('<div class="row-card">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    load_btn = st.button("🔄 加载开奖数据", use_container_width=True)
with col2:
    count = st.slider("往期期数", 20, 100, 50, 10)
st.markdown('</div>', unsafe_allow_html=True)

if load_btn or "lottery_data" not in st.session_state:
    with st.spinner("🎲 正在从福彩官网抓取数据..."):
        data = cached_fetch(count)
        if not data:
            data = load_cache()
            st.warning("⚠️ 网络请求失败，已加载本地缓存数据")
        st.session_state.lottery_data = data

data = st.session_state.get("lottery_data", [])

if data:
    tabs = st.tabs(["📜 往期开奖", "🎯 本期预测", "💎 必中大奖", "📊 统计分析", "🎲 随机生成", "🔍 中奖查询"])

    with tabs[0]:
        st.markdown("### 📜 往期开奖号码")
        st.markdown("---")
        for item in data:
            st.markdown(
                f"""
                <div class="row-card">
                    <span class="issue-badge">第 {item['issue']} 期</span>
                    <span style="color:#FFE4B5;margin-right:15px;">📅 {item['date']}</span>
                    {render_row(item['red'], item['blue'])}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tabs[1]:
        st.markdown("### 🎯 本期精准预测 (5组)")
        st.markdown("---")
        next_issue = calc_next_issue(data[0]["issue"]) if data else ""
        next_date = calc_next_draw_date(data[0]["date"]) if data else ""
        st.markdown(
            f'<div style="text-align:center;color:#FFD700;font-size:16px;">'
            f'📅 第 <span style="font-weight:bold;font-size:20px;">{next_issue}</span> 期　开奖时间：{next_date}</div>',
            unsafe_allow_html=True,
        )

        if st.button("🎲 生成本期预测号码", use_container_width=True, key="gen_predict"):
            preds = generate_prediction(data, 5)
            st.session_state.predictions = preds

        preds = st.session_state.get("predictions", [])
        for idx, p in enumerate(preds):
            combo_str = " ".join(f"{n:02d}" for n in p["red"]) + f" + {p['blue']:02d}"
            st.markdown(
                f"""
                <div class="row-card">
                    <span class="issue-badge">第 {idx + 1} 组</span>
                    {render_row(p['red'], p['blue'], suffix_html=st.session_state.get(f'cp_{idx}', ''))}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.code(combo_str, language="text")

    with tabs[2]:
        st.markdown("### 💎 必中大奖 · 钻石矩阵 (10组)")
        st.markdown("---")
        next_issue = calc_next_issue(data[0]["issue"]) if data else ""
        st.markdown(
            f'<div style="text-align:center;color:#FFD700;font-size:16px;">'
            f'🏆 第 <span style="font-weight:bold;font-size:20px;">{next_issue}</span> 期 · 10大策略全覆盖</div>',
            unsafe_allow_html=True,
        )

        if st.button("🎊 一键生成必中大奖号码", use_container_width=True, key="gen_jackpot"):
            wheel_results, top_red, top_blue = generate_wheel(data, 10)
            st.session_state.wheel_results = wheel_results
            st.session_state.top_red = top_red
            st.session_state.top_blue = top_blue

        wheel_results = st.session_state.get("wheel_results", [])
        if wheel_results:
            for idx, w in enumerate(wheel_results):
                combo_str = " ".join(f"{n:02d}" for n in w["red"]) + f" + {w['blue']:02d}"
                st.markdown(
                    f"""
                    <div class="row-card">
                        <span class="issue-badge">#{idx + 1}</span>
                        <span class="strategy-tag">{w['strategy']}</span><br><br>
                        {render_row(w['red'], w['blue'])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.code(combo_str, language="text")

            if st.session_state.get("top_red"):
                with st.expander("🎁 热号池 Top 16 & 蓝号池 Top 8"):
                    st.markdown("**🔴 热号池 Top 16:**")
                    st.markdown(render_red_balls(st.session_state["top_red"]), unsafe_allow_html=True)
                    st.markdown("**🔵 蓝号池 Top 8:**")
                    st.markdown(
                        " ".join(f'<span class="ball-blue">{n:02d}</span>' for n in st.session_state["top_blue"]),
                        unsafe_allow_html=True,
                    )

    with tabs[3]:
        st.markdown("### 📊 统计分析")
        red_freq, blue_freq = analyze_frequency(data)
        red_missing, blue_missing = analyze_missing(data)
        hot_red, cold_red, hot_blue, cold_blue = analyze_hot_cold(red_freq, blue_freq, 10)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🔥 热门红球 TOP 10")
            st.markdown(render_red_balls(hot_red), unsafe_allow_html=True)
        with col_b:
            st.markdown("#### ❄️ 冷门红球 TOP 10")
            st.markdown(render_red_balls(cold_red), unsafe_allow_html=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("#### 🔵 热门蓝球 TOP 5")
            st.markdown(" ".join(f'<span class="ball-blue">{n:02d}</span>' for n in hot_blue), unsafe_allow_html=True)
        with col_d:
            st.markdown("#### 🥶 冷门蓝球 TOP 5")
            st.markdown(" ".join(f'<span class="ball-blue">{n:02d}</span>' for n in cold_blue), unsafe_allow_html=True)

        st.markdown("#### 📈 全部红球出现频次")
        freq_sorted = sorted(red_freq.items(), key=lambda x: x[1], reverse=True)
        chart_data = {n: f for n, f in freq_sorted}
        st.bar_chart(chart_data, height=300, use_container_width=True)

        st.markdown("#### 📈 全部蓝球出现频次")
        blue_sorted = sorted(blue_freq.items(), key=lambda x: x[1], reverse=True)
        st.bar_chart({n: f for n, f in blue_sorted}, height=250, use_container_width=True)

    with tabs[4]:
        st.markdown("### 🎲 机选随机生成")
        st.markdown("---")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            rand_count = st.number_input("生成几组", 1, 20, 5, 1, key="rand_count")
        with col_b:
            st.caption("🎰 真正随机，每组独立生成 6红 + 1蓝")
        if st.button("🎰 一键随机生成", use_container_width=True, key="gen_random"):
            results = []
            for _ in range(rand_count):
                r = sorted(random.sample(range(1, 34), 6))
                b = random.randint(1, 16)
                results.append({"red": r, "blue": b})
            st.session_state.rand_results = results
        rands = st.session_state.get("rand_results", [])
        for idx, r in enumerate(rands):
            combo_str = " ".join(f"{n:02d}" for n in r["red"]) + f" + {r['blue']:02d}"
            st.markdown(
                f"""
                <div class="row-card">
                    <span class="issue-badge">第 {idx + 1} 组</span>
                    {render_row(r['red'], r['blue'])}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.code(combo_str, language="text")

    with tabs[5]:
        st.markdown("### 🔍 查询中奖 · 多号码智能组合")
        st.markdown("---")
        st.caption("💡 红球最多输入 10 个（至少 6 个），蓝球最多 5 个（至少 1 个），后台自动组合 C(红n,6)×C(蓝m,1) 组彩票逐组校验")

        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            issue_options = [f"第 {item['issue']} 期 ({item['date']})" for item in data]
            default_idx = st.session_state.get("prize_issue_idx", 0)
            issue_label = st.selectbox("选择开奖期号", issue_options, index=default_idx, key="prize_issue_sel")
            st.session_state.prize_issue_idx = issue_options.index(issue_label)
        with col_sel2:
            st.markdown("")
            st.markdown("")
            st.caption(f"✅ 已选：{issue_label}")

        issue_num = issue_label.split(" ")[1]
        win_record = None
        for item in data:
            if item["issue"] == issue_num:
                win_record = item
                break
        if win_record:
            st.markdown(
                f"""
                <div class="row-card">
                    <span class="issue-badge">第 {win_record['issue']} 期开奖</span>
                    📅 {win_record['date']} &nbsp;&nbsp;
                    {render_row(win_record['red'], win_record['blue'])}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🔴 红球（最多 10 个）")
        red_cols = st.columns(5)
        red_inputs = []
        for i in range(10):
            with red_cols[i % 5]:
                val = st.text_input(f"红{i+1}", value="", max_chars=2, key=f"prize_red_{i}", placeholder="00")
                red_inputs.append(val)

        st.markdown("#### 🔵 蓝球（最多 5 个）")
        blue_cols = st.columns(5)
        blue_inputs = []
        for i in range(5):
            with blue_cols[i]:
                val = st.text_input(f"蓝{i+1}", value="", max_chars=2, key=f"prize_blue_{i}", placeholder="00")
                blue_inputs.append(val)

        def _collect_nums(inputs, lo, hi):
            nums = []
            for s in inputs:
                s = s.strip()
                if not s:
                    continue
                try:
                    n = int(s)
                    if lo <= n <= hi:
                        nums.append(n)
                except Exception:
                    pass
            return sorted(set(nums))

        red_list = _collect_nums(red_inputs, 1, 33)
        blue_list = _collect_nums(blue_inputs, 1, 16)

        st.markdown("---")
        col_calc1, col_calc2 = st.columns([1, 3])
        with col_calc1:
            check_btn = st.button("🔍 查询中奖", use_container_width=True, key="do_check")
            clear_btn = st.button("🗑 清空", use_container_width=True, key="do_clear")
        with col_calc2:
            st.caption(f"📌 当前红球池：{len(red_list)} 个 {red_list}")
            st.caption(f"📌 当前蓝球池：{len(blue_list)} 个 {blue_list}")

        if clear_btn:
            for i in range(10):
                st.session_state[f"prize_red_{i}"] = ""
            for i in range(5):
                st.session_state[f"prize_blue_{i}"] = ""
            st.rerun()

        if check_btn:
            if len(red_list) < 6:
                st.warning(f"⚠️ 红球至少 6 个有效号码，当前 {len(red_list)} 个")
            elif len(blue_list) < 1:
                st.warning("⚠️ 蓝球至少 1 个号码")
            elif not win_record:
                st.warning("⚠️ 未找到该期开奖记录")
            else:
                red_combos = list(itertools.combinations(red_list, 6))
                total_combos = len(red_combos) * len(blue_list)
                fixed_money_map = {3: 3000, 4: 200, 5: 10, 6: 5}
                prize_total = 0
                float_cnt = 0
                win_cnt = 0
                results_list = []
                for rc in red_combos:
                    for b in blue_list:
                        r = check_prize(sorted(rc), b, win_record["red"], win_record["blue"])
                        if r["won"]:
                            win_cnt += 1
                            if r["level"] in fixed_money_map:
                                prize_total += fixed_money_map[r["level"]]
                            else:
                                float_cnt += 1
                        results_list.append({
                            "red": sorted(rc), "blue": b,
                            "prize_name": r["name"], "prize_money": r["money"],
                            "red_hit": r["red_match"], "blue_hit": r["blue_match"],
                            "won": r["won"], "level": r["level"],
                        })

                if win_cnt > 0:
                    if float_cnt > 0:
                        st.success(
                            f"🎉 共 **{total_combos}** 组 · 中奖 **{win_cnt}** 组 · "
                            f"固定奖金合计 **¥{prize_total:,}元**（含 {float_cnt} 组浮动奖金）"
                        )
                    else:
                        st.success(
                            f"🎉 共 **{total_combos}** 组 · 中奖 **{win_cnt}** 组 · "
                            f"合计奖金 **¥{prize_total:,}元**"
                        )
                else:
                    st.info(f"😅 共 **{total_combos}** 组，全部未中奖。再接再厉！")

                with st.expander(f"📋 全部 {len(results_list)} 组详情", expanded=(win_cnt > 0)):
                    for idx, r in enumerate(results_list):
                        hit_reds_in_win = [n for n in r["red"] if n in win_record["red"]]
                        hit_blue = r["blue"] == win_record["blue"]
                        row_html = f"""
                        <div class="row-card" style="opacity:{1.0 if r['won'] else 0.7};">
                            <span class="issue-badge" style="background:{'linear-gradient(135deg,#32CD32,#228B22)' if r['won'] else 'linear-gradient(135deg,#888,#555)'};color:white;">
                                {'🏆' if r['won'] else '  '}第{idx+1:02d}组
                            </span>
                            {render_row(r['red'], r['blue'])}
                            <span style="color:#FFD700;margin-left:10px;">
                                中红 {r['red_hit']} · 蓝 {'中' if r['blue_hit'] else '-'}
                            </span>
                            <span style="color:{'#32CD32' if r['won'] else '#aaa'};margin-left:10px;font-weight:bold;">
                                {r['prize_name']}{'  ' + r['prize_money'] if r['won'] else ''}
                            </span>
                        </div>
                        """
                        st.markdown(row_html, unsafe_allow_html=True)

                st.markdown(
                    "<div class='footer-tip'>📖 中奖规则：一等奖(6+1) 二等奖(6+0) 三等奖(5+1) 四等奖(5+0/4+1) 五等奖(4+0/3+1) 六等奖(2+1/1+1/0+1)</div>",
                    unsafe_allow_html=True,
                )

else:
    st.info("👆 点击上方「🔄 加载开奖数据」按钮开始")

st.markdown("---")
st.markdown(
    '<div class="footer-tip">🎊 数据仅供娱乐参考，请理性购彩 · 祝君好运 🎊</div>',
    unsafe_allow_html=True,
)
