import time
import datetime
import os
import sys
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# --- CONFIGURATION ---
SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
CALENDAR_ID = 'primary'
TIMEZONE = 'Asia/Tokyo'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_PATH = '/app/config/credentials.json'
TOKEN_PATH = '/app/config/token.json'

# --- 🧠 SMART MAPPING SECTION ---
# Add your keywords here! (Lowercase please)
KEYWORD_MAP = {

    # =========================
    # 会議・打ち合わせ系 👥
    # =========================
    "mtg": ":busts_in_silhouette:",
    "meeting": ":meeting:",
    "meet": ":meeting:",
    "sync": ":repeat:",
    "1on1": ":bust_in_silhouette:",
    "one-on-one": ":bust_in_silhouette:",
    "review": ":mag:",
    "discussion": ":speech_balloon:",
    "打ち合わせ": ":busts_in_silhouette:",
    "会議": ":busts_in_silhouette:",
    "定例": ":repeat:",
    "全体会": ":busts_in_silhouette:",
    "面談": ":bust_in_silhouette:",
    "ヒアリング": ":ear:",
    "調整": ":wrench:",
    "相談": ":speech_balloon:",

    # =========================
    # オンライン会議・通話 📹📞
    # =========================
    "zoom": ":video_camera:",
    "teams": ":video_camera:",
    "google meet": ":video_camera:",
    "webex": ":video_camera:",
    "online": ":globe_with_meridians:",
    "remote": ":house_with_garden:",
    "call": ":phone:",
    "電話": ":phone:",
    "通話": ":phone:",

    # =========================
    # 休暇・不在 🌴🏠😴
    # =========================
    "休み": ":house:",
    "休暇": ":palm_tree:",
    "年休": ":palm_tree:",
    "有給": ":palm_tree:",
    "代休": ":palm_tree:",
    "厚生休暇": ":palm_tree:",
    "vacation": ":palm_tree:",
    "holiday": ":palm_tree:",
    "off": ":palm_tree:",
    "leave": ":palm_tree:",
    "不在": ":no_entry_sign:",
    "out of office": ":ooo:",
    "ooo": ":ooo:",
    "private": ":lock:",
    "病欠": ":face_with_thermometer:",
    "体調不良": ":face_with_thermometer:",

    # =========================
    # 出張・移動 🚄✈️💼
    # =========================
    "出張": ":briefcase:",
    "travel": ":airplane:",
    "移動": ":train:",
    "移動中": ":train:",
    "現地": ":round_pushpin:",
    "on-site": ":round_pushpin:",
    "onsite": ":round_pushpin:",
    "flight": ":airplane:",
    "airport": ":airplane:",
    "新幹線": ":bullettrain_side:",
    "電車": ":train:",
    "バス": ":bus:",

    # =========================
    # 実験・研究・開発 🔬⚗️📈
    # =========================
    "実験": ":alembic:",
    "計測": ":chart_with_upwards_trend:",
    "測定": ":straight_ruler:",
    "実装": ":hammer_and_wrench:",
    "開発": ":computer:",
    "研究": ":microscope:",
    "analysis": ":bar_chart:",
    "解析": ":bar_chart:",
    "データ解析": ":bar_chart:",
    "dataset": ":file_folder:",
    "annotation": ":label:",
    "training": ":brain:",
    "学習": ":brain:",
    "評価": ":white_check_mark:",
    "検証": ":white_check_mark:",
    "debug": ":bug:",
    "デバッグ": ":bug:",

    # =========================
    # 授業・教育・指導 🎓📚
    # =========================
    "lecture": ":mortar_board:",
    "class": ":mortar_board:",
    "授業": ":mortar_board:",
    "講義": ":mortar_board:",
    "演習": ":pencil:",
    "ゼミ": ":books:",
    "seminar": ":books:",
    "指導": ":teacher:",
    "TA": ":teacher:",
    "mentoring": ":teacher:",

    # =========================
    # 発表・イベント 🎤🎉
    # =========================
    "presentation": ":microphone:",
    "発表": ":microphone:",
    "登壇": ":microphone:",
    "conference": ":stadium:",
    "学会": ":stadium:",
    "workshop": ":hammer:",
    "イベント": ":sparkles:",
    "説明会": ":information_source:",

    # =========================
    # 食事・休憩 🍱☕
    # =========================
    "lunch": ":bento:",
    "昼休み": ":bento:",
    "昼食": ":bento:",
    "break": ":coffee:",
    "休憩": ":coffee:",
    "coffee": ":coffee:",
    "dinner": ":fork_and_knife:",
    "飲み会": ":beer:",
    "忘年会": ":beer:",
    "新年会": ":beer:",
    "懇親会": ":clinking_glasses:",

    # =========================
    # 集中作業・個人作業 🧠🎧
    # =========================
    "focus": ":headphones:",
    "deep work": ":headphones:",
    "集中": ":headphones:",
    "作業": ":keyboard:",
    "writing": ":memo:",
    "執筆": ":memo:",
    "paper": ":page_facing_up:",
    "論文": ":page_facing_up:",
    "reading": ":book:",
    "読書": ":book:",

}
DEFAULT_EMOJI = ":calendar:"  # 📅 Default if no keyword matches


def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            print("❌ No valid token found! You must generate token.json locally first.")
            sys.exit(1)

    return build('calendar', 'v3', credentials=creds)


def get_smart_emoji(title):
    """Checks the event title against keywords to pick an icon."""
    title_lower = title.lower()

    for keyword, emoji in KEYWORD_MAP.items():
        if keyword in title_lower:
            return emoji

    return DEFAULT_EMOJI


def set_slack_status(client, text, emoji):
    try:
        # Check current status first to avoid API spam
        current = client.users_profile_get()['profile']
        current_text = current.get('status_text', '')
        current_emoji = current.get('status_emoji', '')

        if current_text != text or current_emoji != emoji:
            client.users_profile_set(
                profile={
                    "status_text": text,
                    "status_emoji": emoji,
                    "status_expiration": 0
                }
            )
            print(f"✅ Status Updated: {text} {emoji}")
        # else: print("💤 Status unchanged.")

    except SlackApiError as e:
        print(f"⚠️ Slack API Error: {e.response['error']}")


def main():
    print("🚀 Bot started with Smart Mapping...")
    slack_client = WebClient(token=SLACK_TOKEN)
    tz = pytz.timezone(TIMEZONE)

    while True:
        try:
            service = get_calendar_service()
            now = datetime.datetime.now(tz)

            # Check for events active NOW
            time_min = now.isoformat()
            time_max = (now + datetime.timedelta(minutes=1)).isoformat()

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if events:
                event = events[0]
                title = event.get('summary', 'Meeting')

                # Check privacy
                if event.get('visibility') == 'private':
                    title = "Busy"
                    icon = ":lock:"
                else:
                    # Pick the smart icon based on the title!
                    icon = get_smart_emoji(title)

                set_slack_status(slack_client, title, icon)
            else:
                set_slack_status(slack_client, "", "")

        except Exception as e:
            print(f"🔥 Error in main loop: {e}")

        sys.stdout.flush()
        time.sleep(60)


if __name__ == '__main__':
    main()