import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"  # FastAPI 서버 주소

st.title("🎬 Movie Archive")

# 영화 추가
st.header("영화 추가")
def submit_movie():
    payload = {
        "title": st.session_state["title"],
        "release_date": st.session_state["release_date"],
        "director": st.session_state["director"],
        "genre": st.session_state["genre"],
        "poster_url": st.session_state["poster_url"],
    }
    res = requests.post(f"{API_URL}/movies/", json=payload)
    if res.status_code == 200:
        st.success("영화 등록 완료!")
        for k in ["title", "release_date", "director", "genre", "poster_url"]:
            st.session_state[k] = ""
    else:
        st.error("등록 실패")

with st.form("add_movie"):
    st.text_input("제목", key="title")
    st.text_input("개봉일 (YYYY-MM-DD)", key="release_date")
    st.text_input("감독", key="director")
    st.text_input("장르", key="genre")
    st.text_input("포스터 URL", key="poster_url")
    st.form_submit_button("등록하기", on_click=submit_movie)


# 영화 목록
st.header("영화 목록")
res = requests.get(f"{API_URL}/movies/")
if res.status_code == 200:
    movies = res.json()
    cols_per_row = 3
    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, m in enumerate(movies[i:i+cols_per_row]):
            with cols[j]:
                st.image(m.get("poster_url") or "https://via.placeholder.com/150", width=150)
                st.write(f"**{m['title']}**")
                st.write(f"개봉일: {m.get('release_date', '-')}")
                st.write(f"감독: {m.get('director', '-')}")
                st.write(f"장르: {m.get('genre', '-')}")
                st.divider()
else:
    st.error("영화 목록을 불러올 수 없습니다.")


# 리뷰 등록
st.header("리뷰 등록")

if movies:
    movie_map = {m["title"]: m["id"] for m in movies}

    def submit_review():
        payload = {
            "movie_id": movie_map[st.session_state["movie_choice"]],
            "author": st.session_state["review_author"],
            "content": st.session_state["review_content"]
        }
        res_review = requests.post(f"{API_URL}/reviews/", json=payload)
        if res_review.status_code == 200:
            st.success("리뷰 등록 완료!")
            # 제출 후 입력 초기화
            st.session_state["review_author"] = ""
            st.session_state["review_content"] = ""
        else:
            st.error("리뷰 등록 실패")

    with st.form("add_review"):
        st.selectbox("영화 선택", list(movie_map.keys()), key="movie_choice")
        st.text_input("작성자 이름", key="review_author", value="")
        st.text_area("리뷰 내용", key="review_content", value="")
        st.form_submit_button("리뷰 등록", on_click=submit_review)


# 최근 리뷰 10개 표시
st.header("최근 리뷰")

if movies:
    all_reviews = []

    for m in movies:
        res_r = requests.get(f"{API_URL}/reviews/{m['id']}")
        if res_r.status_code == 200:
            reviews = res_r.json()
            for r in reviews:
                r_with_title = r.copy()
                r_with_title["movie_title"] = m["title"]
                all_reviews.append(r_with_title)

    # created_at 기준 내림차순 정렬
    all_reviews.sort(key=lambda x: x["created_at"], reverse=True)

    for r in all_reviews[:10]:
        created_str = datetime.fromisoformat(r["created_at"]).strftime("%Y-%m-%d %H:%M")
        st.write(f"**{r['movie_title']}** - {r['author']} ({created_str})")
        st.write(r["content"])
        st.divider()
else:
    st.info("등록된 영화가 없으면 리뷰도 표시되지 않습니다.")
