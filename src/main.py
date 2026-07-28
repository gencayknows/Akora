import flet as ft
import time
import threading

def main(page: ft.Page):
    page.title = "Akura"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0813"  # Deep eggplant background
    page.padding = 0
    page.spacing = 0
    page.window_width = 1100
    page.window_height = 750
    page.window_min_width = 750
    page.window_min_height = 550

    # Color Tokens
    BG_MAIN = "#0B0813"
    BG_SIDEBAR = "#07050E"
    CARD_BG = "#160F22"
    CARD_HOVER = "#231835"
    BRONZE_ACCENT = "#C5A059"
    BRONZE_LIGHT = "#E5C178"
    TEXT_PRIMARY = "#F3F0F8"
    TEXT_MUTED = "#8A7E99"

    songs_queue = [
        {"title": "Starboy", "artist": "The Weeknd", "duration": 230, "img": "https://picsum.photos/200?random=1"},
        {"title": "Midnight City", "artist": "M83", "duration": 243, "img": "https://picsum.photos/200?random=2"},
        {"title": "As It Was", "artist": "Harry Styles", "duration": 167, "img": "https://picsum.photos/200?random=3"},
        {"title": "Nightcall", "artist": "Kavinsky", "duration": 259, "img": "https://picsum.photos/200?random=4"},
        {"title": "Blinding Lights", "artist": "The Weeknd", "duration": 200, "img": "https://picsum.photos/200?random=5"},
        {"title": "Sweater Weather", "artist": "The Neighbourhood", "duration": 240, "img": "https://picsum.photos/200?random=6"},
    ]

    state = {
        "is_playing": False,
        "current_index": 0,
        "progress": 0.0,
        "volume": 80.0,
        "selected_nav": "Home",
        "liked_indices": {0, 2},
        "is_seeking": False,
        "selected_playlist": None,
    }

    playlists_data = [
        {
            "name": "Jazz Playlist",
            "desc": "Smooth late-night sax & chill acoustic jazz vibes",
            "count": "14 tracks",
            "img": "https://picsum.photos/300?random=10",
            "songs": [0, 1, 3]
        },
        {
            "name": "Gym Playlist",
            "desc": "High bpm energetic beats for heavy workout sessions",
            "count": "22 tracks",
            "img": "https://picsum.photos/300?random=11",
            "songs": [2, 4, 5]
        },
        {
            "name": "Chill Vibes",
            "desc": "Relaxing lo-fi and indie melodies to unwind",
            "count": "18 tracks",
            "img": "https://picsum.photos/300?random=12",
            "songs": [1, 2, 5]
        },
    ]

    def format_seconds(secs):
        m = int(secs) // 60
        s = int(secs) % 60
        return f"{m}:{s:02d}"

    def get_current_song():
        return songs_queue[state["current_index"]]

    player_image = ft.Image(
        src=get_current_song()["img"],
        width=56,
        height=56,
        border_radius=ft.BorderRadius(8, 8, 8, 8),
        fit="cover"
    )
    player_title = ft.Text(get_current_song()["title"], size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, no_wrap=True)
    player_artist = ft.Text(get_current_song()["artist"], size=12, color=TEXT_MUTED, no_wrap=True)

    play_pause_icon = ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=28, color="#0B0813")

    time_current_text = ft.Text(format_seconds(state["progress"]), size=11, color=TEXT_MUTED)
    time_total_text = ft.Text(format_seconds(get_current_song()["duration"]), size=11, color=TEXT_MUTED)

    volume_text = ft.Text(f"{int(state['volume'])}%", size=12, color=TEXT_MUTED, width=38)
    volume_icon = ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, color=TEXT_MUTED, size=20)

    progress_slider = ft.Slider(
        value=state["progress"],
        min=0,
        max=get_current_song()["duration"],
        active_color=BRONZE_ACCENT,
        inactive_color="#261B3B",
        thumb_color=BRONZE_LIGHT,
        expand=True,
    )

    def on_slider_change_start(e):
        state["is_seeking"] = True

    def on_slider_change(e):
        state["progress"] = float(e.control.value)
        time_current_text.value = format_seconds(state["progress"])
        page.update()

    def on_slider_change_end(e):
        state["progress"] = float(e.control.value)
        state["is_seeking"] = False
        page.update()

    progress_slider.on_change_start = on_slider_change_start
    progress_slider.on_change = on_slider_change
    progress_slider.on_change_end = on_slider_change_end

    def on_volume_change(e):
        state["volume"] = float(e.control.value)
        volume_text.value = f"{int(state['volume'])}%"
        if state["volume"] == 0:
            volume_icon.name = ft.Icons.VOLUME_OFF_ROUNDED
        elif state["volume"] < 50:
            volume_icon.name = ft.Icons.VOLUME_DOWN_ROUNDED
        else:
            volume_icon.name = ft.Icons.VOLUME_UP_ROUNDED
        volume_text.update()
        volume_icon.update()

    def update_player_ui():
        song = get_current_song()
        player_title.value = song["title"]
        player_artist.value = song["artist"]
        player_image.src = song["img"]
        progress_slider.max = song["duration"]
        progress_slider.value = min(state["progress"], song["duration"])
        time_current_text.value = format_seconds(state["progress"])
        time_total_text.value = format_seconds(song["duration"])
        play_pause_button.icon = ft.Icons.PAUSE_ROUNDED if state["is_playing"] else ft.Icons.PLAY_ARROW_ROUNDED
        like_button.icon = ft.Icons.FAVORITE_ROUNDED if state["current_index"] in state["liked_indices"] else ft.Icons.FAVORITE_BORDER_ROUNDED
        like_button.icon_color = BRONZE_ACCENT if state["current_index"] in state["liked_indices"] else TEXT_MUTED

        render_sidebar()
        if state["selected_nav"] in ["Home", "Playlists"]:
            render_main_view()
        else:
            page.update()

    # FIX: page.update() is now correctly INSIDE toggle_play (it was
    # accidentally dedented in your version, so it only ran once at
    # startup instead of every time you pressed play/pause).
    def toggle_play(e=None):
        state["is_playing"] = not state["is_playing"]

        play_pause_button.icon = (
            ft.Icons.PAUSE_ROUNDED
            if state["is_playing"]
            else ft.Icons.PLAY_ARROW_ROUNDED
        )
        page.update()

    def play_next(e=None):
        state["current_index"] = (state["current_index"] + 1) % len(songs_queue)
        state["progress"] = 0
        state["is_seeking"] = False
        update_player_ui()

    def play_prev(e=None):
        state["current_index"] = (state["current_index"] - 1) % len(songs_queue)
        state["progress"] = 0
        state["is_seeking"] = False
        update_player_ui()

    def toggle_like_current(e=None):
        idx = state["current_index"]
        if idx in state["liked_indices"]:
            state["liked_indices"].remove(idx)
        else:
            state["liked_indices"].add(idx)
        update_player_ui()

    like_button = ft.IconButton(
        icon=ft.Icons.FAVORITE_ROUNDED if state["current_index"] in state["liked_indices"] else ft.Icons.FAVORITE_BORDER_ROUNDED,
        icon_color=BRONZE_ACCENT if state["current_index"] in state["liked_indices"] else TEXT_MUTED,
        icon_size=20,
        on_click=toggle_like_current,
        tooltip="Like"
    )

    def play_song_at_index(idx):
        if state["current_index"] == idx:
            toggle_play()
            return

        state["current_index"] = idx
        state["progress"] = 0
        state["is_playing"] = True
        state["is_seeking"] = False

        update_player_ui()

    main_view_container = ft.Container(expand=True, padding=ft.Padding(25, 10, 25, 20))

    def create_nav_button(text, icon_name):
        is_selected = state["selected_nav"] == text
        return ft.Container(
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=8,
            bgcolor=CARD_HOVER if is_selected else "transparent",
            content=ft.Row([
                ft.Icon(icon_name, size=20, color=BRONZE_ACCENT if is_selected else TEXT_MUTED),
                ft.Text(text, size=14, weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL, color=TEXT_PRIMARY if is_selected else TEXT_MUTED)
            ], spacing=12),
            on_click=lambda e, name=text: switch_tab(name),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)
        )

    sidebar_nav_col = ft.Column(spacing=6)
    account_nav_button = ft.Container()

    def render_sidebar():
        sidebar_nav_col.controls = [
            create_nav_button("Home", ft.Icons.HOME_ROUNDED),
            create_nav_button("Playlists", ft.Icons.QUEUE_MUSIC_ROUNDED),
            create_nav_button("Liked Songs", ft.Icons.FAVORITE_ROUNDED),
            create_nav_button("Downloads", ft.Icons.DOWNLOAD_ROUNDED),
        ]

        is_acc_selected = state["selected_nav"] == "Account"
        account_nav_button.content = ft.Row([
            ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=24, color=BRONZE_ACCENT if is_acc_selected else TEXT_MUTED),
            ft.Column([
                ft.Text("Akura Listener", size=13, weight=ft.FontWeight.BOLD if is_acc_selected else ft.FontWeight.NORMAL, color=TEXT_PRIMARY if is_acc_selected else TEXT_MUTED)
            ], spacing=0)
        ], spacing=10)
        account_nav_button.padding = ft.Padding(12, 10, 12, 10)
        account_nav_button.border_radius = 8
        account_nav_button.bgcolor = CARD_HOVER if is_acc_selected else "transparent"
        account_nav_button.on_click = lambda e: switch_tab("Account")

    def get_home_view():
        recent_cards = []
        for idx, s in enumerate(songs_queue):
            recent_cards.append(
                ft.Container(
                    width=150,
                    padding=10,
                    border_radius=10,
                    bgcolor=CARD_BG,
                    content=ft.Column([
                        ft.Image(src=s["img"], width=130, height=130, border_radius=ft.BorderRadius(8,8,8,8), fit="cover"),
                        ft.Text(s["title"], size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, no_wrap=True),
                        ft.Text(s["artist"], size=11, color=TEXT_MUTED, no_wrap=True),
                    ], spacing=6),
                    on_click=lambda e, i=idx: play_song_at_index(i)
                )
            )

        song_rows = []
        for idx, s in enumerate(songs_queue):
            song_rows.append(
                ft.Container(
                    padding=ft.Padding(10, 8, 10, 8),
                    border_radius=8,
                    bgcolor=CARD_BG if idx == state["current_index"] else "transparent",
                    content=ft.Row([
                        ft.Image(src=s["img"], width=42, height=42, border_radius=ft.BorderRadius(6,6,6,6), fit="cover"),
                        ft.Column([
                            ft.Text(s["title"], size=13, weight=ft.FontWeight.BOLD, color=BRONZE_LIGHT if idx == state["current_index"] else TEXT_PRIMARY),
                            ft.Text(s["artist"], size=11, color=TEXT_MUTED)
                        ], expand=True, spacing=2),
                        ft.Text(format_seconds(s["duration"]), size=12, color=TEXT_MUTED),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW_ROUNDED if not (state["is_playing"] and idx == state["current_index"]) else ft.Icons.PAUSE_ROUNDED,
                            icon_color=BRONZE_ACCENT,
                            icon_size=20,
                            on_click=lambda e, i=idx: play_song_at_index(i)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    on_click=lambda e, i=idx: play_song_at_index(i)
                )
            )

        return ft.ListView(
            expand=True,
            spacing=20,
            controls=[
                ft.Text("Recently Played", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Row(recent_cards, scroll=ft.ScrollMode.AUTO, spacing=14),
                ft.Text("Recommended Tracks", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Column(song_rows, spacing=4)
            ]
        )

    def get_playlists_view():
        playlist_cards = []
        for pl in playlists_data:
            playlist_cards.append(
                ft.Container(
                    padding=16,
                    border_radius=12,
                    bgcolor=CARD_BG,
                    content=ft.Row([
                        ft.Image(src=pl["img"], width=80, height=80, border_radius=ft.BorderRadius(8,8,8,8), fit="cover"),
                        ft.Column([
                            ft.Text(pl["name"], size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(pl["desc"], size=12, color=TEXT_MUTED, no_wrap=True),
                            ft.Text(pl["count"], size=11, color=BRONZE_ACCENT)
                        ], spacing=4, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                            icon_color=BRONZE_ACCENT,
                            icon_size=36,
                            on_click=lambda e, song_idx=pl["songs"][0]: play_song_at_index(song_idx)
                        )
                    ], spacing=16, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    on_click=lambda e, song_idx=pl["songs"][0]: play_song_at_index(song_idx)
                )
            )

        return ft.ListView(
            expand=True,
            spacing=16,
            controls=[
                ft.Text("Your Playlists", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Column(playlist_cards, spacing=12)
            ]
        )

    def get_account_view():
        return ft.Column([
            ft.Text("User Account", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=10),
            ft.Container(
                padding=20,
                border_radius=12,
                bgcolor=CARD_BG,
                content=ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=64, color=BRONZE_ACCENT),
                    ft.Column([
                        ft.Text("Akura Listener", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("user@akura.io", size=13, color=TEXT_MUTED)
                    ], spacing=4)
                ], spacing=16)
            )
        ])

    def get_liked_view():
        controls = [ft.Text("Liked Songs", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)]
        liked_count = 0
        for i, s in enumerate(songs_queue):
            if i in state["liked_indices"]:
                liked_count += 1
                controls.append(
                    ft.ListTile(
                        leading=ft.Image(src=s["img"], width=44, height=44, fit="cover", border_radius=ft.BorderRadius(6,6,6,6)),
                        title=ft.Text(s["title"], color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(s["artist"], color=TEXT_MUTED),
                        trailing=ft.Text(format_seconds(s["duration"]), color=TEXT_MUTED),
                        on_click=lambda e, idx=i: play_song_at_index(idx)
                    )
                )
        if liked_count == 0:
            controls.append(ft.Text("No liked songs yet. Tap the heart button on any track!", color=TEXT_MUTED))
        return ft.ListView(controls=controls, expand=True, spacing=8)

    def get_downloads_view():
        return ft.Column([
            ft.Text("Offline Downloads", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=15),
            ft.Text("Offline cache status:", size=13, color=TEXT_MUTED),
            ft.Container(height=5),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DOWNLOAD_DONE_ROUNDED, color=BRONZE_ACCENT),
                title=ft.Text("Starboy - The Weeknd", color=TEXT_PRIMARY),
                subtitle=ft.Text("Downloaded • 8.4 MB", color=TEXT_MUTED)
            )
        ])

    def render_main_view():
        if state["selected_nav"] == "Home":
            main_view_container.content = get_home_view()
        elif state["selected_nav"] == "Playlists":
            main_view_container.content = get_playlists_view()
        elif state["selected_nav"] == "Account":
            main_view_container.content = get_account_view()
        elif state["selected_nav"] == "Liked Songs":
            main_view_container.content = get_liked_view()
        elif state["selected_nav"] == "Downloads":
            main_view_container.content = get_downloads_view()
        page.update()

    def switch_tab(tab_name):
        state["selected_nav"] = tab_name
        render_sidebar()
        render_main_view()
        update_player_ui()

    sidebar = ft.Container(
        width=230,
        bgcolor=BG_SIDEBAR,
        padding=ft.Padding(18, 24, 18, 20),
        border=ft.Border(right=ft.BorderSide(1, "#181024")),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.GRAPHIC_EQ_ROUNDED, color=BRONZE_ACCENT, size=28),
                ft.Text("Akura", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
            ], spacing=10),
            ft.Container(height=20),
            sidebar_nav_col,
            ft.Container(expand=True),
            account_nav_button
        ])
    )

    search_bar = ft.Container(
        padding=ft.Padding(25, 20, 25, 10),
        content=ft.TextField(
            hint_text="Search songs, artists, playlists...",
            prefix_icon=ft.Icons.SEARCH,
            bgcolor=CARD_BG,
            border_radius=25,
            border_color="transparent",
            focused_border_color=BRONZE_ACCENT,
            content_padding=12,
            text_size=13,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
        )
    )

    play_pause_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        icon_size=28,
        icon_color="#0B0813",
        bgcolor=BRONZE_ACCENT,
        on_click=toggle_play,
    )

    player_bar = ft.Container(
        padding=ft.Padding(20, 10, 20, 14),
        bgcolor=CARD_BG,
        border=ft.Border(top=ft.BorderSide(1, "#251B38")),
        content=ft.Column([
            ft.Row([
                time_current_text,
                progress_slider,
                time_total_text
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Row([
                ft.Row([
                    player_image,
                    ft.Column([
                        player_title,
                        player_artist
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    like_button
                ], spacing=12),

                ft.Row([
                    ft.IconButton(ft.Icons.SKIP_PREVIOUS_ROUNDED, icon_color=TEXT_PRIMARY, icon_size=26, on_click=play_prev),
                    play_pause_button,
                    ft.IconButton(ft.Icons.SKIP_NEXT_ROUNDED, icon_color=TEXT_PRIMARY, icon_size=26, on_click=play_next),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),

                ft.Row([
                    volume_icon,
                    ft.Container(
                        width=100,
                        content=ft.Slider(
                            value=state["volume"],
                            min=0,
                            max=100,
                            active_color=BRONZE_ACCENT,
                            inactive_color="#261B3B",
                            thumb_color=BRONZE_LIGHT,
                            on_change=on_volume_change
                        )
                    ),
                    volume_text
                ], spacing=8, alignment=ft.MainAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], spacing=2)
    )

    render_sidebar()
    render_main_view()

    page.add(
        ft.Column([
            ft.Row([
                sidebar,
                ft.Column([
                    search_bar,
                    main_view_container
                ], expand=True, spacing=0)
            ], expand=True, spacing=0),
            player_bar
        ], expand=True, spacing=0)
    )

    # FIX: `page.call_from_thread` does not exist in Flet — Page has no
    # such attribute, which is exactly the AttributeError you hit.
    # Flet's supported pattern is simply calling page.update() (or
    # control.update()) straight from a background thread, so `refresh()`
    # is now just called directly instead of being wrapped in that call.
    def timer_loop():
        while True:
            time.sleep(0.1)

            if not state["is_playing"]:
                continue
            if state["is_seeking"]:
                continue

            song = get_current_song()
            state["progress"] += 0.1

            if state["progress"] >= song["duration"]:
                play_next()
                continue

            progress_slider.value = state["progress"]
            time_current_text.value = format_seconds(state["progress"])

            try:
                progress_slider.update()
                time_current_text.update()
            except Exception as ex:
                print("Timer UI update failed:", ex)

    threading.Thread(target=timer_loop, daemon=True).start()

ft.app(target=main)