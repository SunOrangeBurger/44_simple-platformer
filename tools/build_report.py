"""Build the Lab 4 report from repository evidence using ReportLab."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
    Preformatted,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/Lab_4_Simple_Platformer_Report.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles["Title"].fontSize = 29
styles["Title"].leading = 34
styles["Title"].textColor = colors.HexColor("#123047")
styles["Heading1"].textColor = colors.HexColor("#123047")
styles["Heading2"].textColor = colors.HexColor("#087f8c")
styles["BodyText"].leading = 14
styles["BodyText"].spaceAfter = 8
styles.add(ParagraphStyle(name="Note", fontSize=8, leading=11,
                          textColor=colors.HexColor("#52616b"), spaceAfter=8))
styles.add(ParagraphStyle(name="ReportCode", fontName="Courier", fontSize=7.4,
                          leading=10, spaceAfter=8))
def p(text, style="BodyText"):
    return Paragraph(text, styles[style])
def page(title):
    return [PageBreak(), p(title, "Heading1"), Spacer(1, 8)]
def table(rows, widths):
    t = Table([[p(escape(str(c)), "Note") for c in row] for row in rows],
              colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceff1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#cbd5e1")),
    ]))
    return t
def screenshot(name, caption, width=480):
    im = Image(str(ROOT / "evidence" / name), width=width, height=width*500/800)
    return [im, Spacer(1, 7), p(caption, "Note")]
def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(48, 40, 547, 40)
    canvas.setFillColor(colors.HexColor("#52616b"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(48, 28, "LAB 4  |  Simple Platformer  |  16 November 2026")
    canvas.drawRightString(547, 28, str(doc.page))

s = [p("SOFTWARE ENGINEERING  /  LAB 4", "Note"), Spacer(1, 18),
     p("Simple Platformer<br/>Implementation Report", "Title"), Spacer(1, 18),
     p("<b>Name:</b> Arun Hariharan<br/><b>SRN:</b> PES2UG24AM126"),
     p('Repository: <link href="https://github.com/SunOrangeBurger/44_simple-platformer" '
       'color="#087f8c">SunOrangeBurger/44_simple-platformer</link>'),
     p("Starting review revision: 734eed5. Original starter: 140ee4d.", "Note"),
     Spacer(1, 12), p("Objective", "Heading2"),
     p("Analyze and complete a real-time Pygame platformer using an LLM as a debugging partner. "
       "The four tasks are reliable platform landings, a graphical Game Over state, replay with "
       "difficulty selection, and sound feedback for jumping, reaching the goal and dying."),
     p("Outcome", "Heading2"),
     p("The repository already contained implementations of all four tasks. This review verifies "
       "the existing work, corrects two sound defects, replaces an ineffective restart test, "
       "and adds targeted regression checks. The final automated suite passes all 13 cases."),
     table([["Task", "Implementation and evidence"],
            ["1. Collision", "Previous/current bottom-edge crossing test; starter/final comparison."],
            ["2. Game Over", "Hazard and bottom-of-screen death; final-score overlay; updates freeze."],
            ["3. Replay", "1/2/3 select Easy/Medium/Hard; Esc exits from Game Over."],
            ["4. Sound", "Generated jump, goal and hit tones; mixer-aware audio format." ]], [105, 394]),
     Spacer(1, 12), p("Evidence scope", "Heading2"),
     p("Tests and screenshots were captured with SDL dummy video/audio drivers on Windows, "
       "Python 3.11.14, Pygame 2.6.1 and pytest 9.2.0. The screenshots are actual Pygame "
       "surface renders from controlled engine states. They are not a human gameplay recording; "
       "the sound was checked programmatically, not by listening.", "Note")]
s += page("1. Architecture and interaction")
s += [p("main.py owns the 800 x 500 window, event loop and 60 FPS clock. GameEngine owns "
        "level objects, physics, scoring, game state, rendering and sound. Player stores motion "
        "and grounded state; Platform and Hazard expose rectangular collision geometry."),
      p("While playing, Left/Right or A/D set horizontal velocity. Space, Up or W starts a jump "
        "only when grounded. Gravity increases downward velocity each frame. Reaching x = 740 "
        "adds one point and returns the player to the start."),
      table([["State", "Trigger", "Result"],
             ["Playing", "Hazard overlap or player y > 500", "Freeze updates; play hit tone; show final score."],
             ["Game Over", "1 / 2 / 3", "Reset score, position and velocity; apply difficulty; resume."],
             ["Game Over", "Esc", "Leave loop and call pygame.quit()."],
             ["Either state", "Window close", "Terminate cleanly."]], [80, 177, 242]),
      Spacer(1, 12)]
s += screenshot("level.png", "Figure 1. Initial level rendered by the final engine: platforms, hazard, goal and visible score.", width=400)
s += [p("Difficulty settings (per simulation frame)", "Heading2"),
      table([["Difficulty", "Gravity", "Horizontal speed", "Jump velocity"],
             ["Easy", "0.45", "4", "-11"], ["Medium", "0.60", "4", "-12"],
             ["Hard", "0.75", "5", "-13"]], [125, 100, 140, 134])]
s += page("2. Collision defect and verification")
s += [p("The starter checks overlap only after movement. A sufficiently fast fall can move "
        "the entire player rectangle below a thin platform in one frame, so no overlap remains "
        "to detect. The existing Task 1 repair instead checks whether the bottom edge crossed "
        "the platform top while descending, together with horizontal overlap."),
      Preformatted("descending: vy >= 0\nprevious bottom <= platform top + 1\ncurrent bottom >= platform top\ncurrent right > platform left\ncurrent left < platform right", styles["ReportCode"]),
      p("When these conditions hold, set y = platform top - player height, set vy = 0 and "
        "mark the player grounded. This detects a skipped platform without requiring a terminal "
        "velocity cap. A rising player is not snapped onto the top."),
      p("Controlled before/after experiment", "Heading2"),
      p("Both versions receive x = 40, y = 420, vy = 90, a 32-pixel player height, and one "
        "platform at y = 460. With gravity 0.6, the tentative new y is 510.6. The player "
        "crosses the platform top without ending inside its rectangle."),
      table([["Version", "Final y", "Final vy", "Grounded", "Game Over"],
             ["Starter 140ee4d", "510.6", "90.6", "False", "True"],
             ["Final", "428", "0", "True", "False"]], [139, 90, 90, 90, 90]),
      Spacer(1, 12), p("The final y is exactly 460 - 32 = 428. The measured outcome confirms "
        "the fast-fall defect in the starter and the corrected landing in the final engine. "
        "tools/capture_evidence.py loads the starter directly from Git history and writes "
        "the raw values to evidence/collision_comparison.txt."),
      p("Review boundaries", "Heading2"),
      p("This is a vertical crossing check for the supplied level, not continuous collision "
        "detection for arbitrary motion. Horizontal overlap is tested at the final position; "
        "platforms are processed in list order. The supplied level uses low horizontal speeds "
        "and separated platforms. Arbitrary high-speed horizontal motion and swept hazard "
        "collisions would require further work."),
      p("Existing implementation history", "Heading2"),
      table([["Commit", "Task recorded in repository history"],
             ["390c0b1", "Task 1: fix collision detection"],
             ["f83ec16", "Task 2: add game over screen"],
             ["45ad1c7", "Task 3: add replay and difficulty options"],
             ["d4e3dbb", "Task 4: add sound feedback"]], [100, 399])]
s += page("3. Game Over, replay and sound")
s += screenshot("game_over.png", "Figure 2. Controlled hazard collision with score set to 2: the engine shows Game Over, final score and replay/exit keys.")
s += [p("Replay behavior", "Heading2"),
      p("The Game Over state retains the final score and ignores normal movement updates. "
        "restart() applies the selected difficulty, resets the score to zero and constructs "
        "a fresh player at the start with zero velocity. Tests exercise all three settings "
        "and confirm that an unknown difficulty falls back to Medium."),
      p("Sound review and corrections", "Heading2"),
      p("The engine synthesizes sine-wave effects without external asset files: jump at "
        "440 Hz for 80 ms, goal at 740 Hz for 110 ms, and hit at 190 Hz for 200 ms. "
        "Previously, buffers assumed 22,050 Hz mono audio even though pygame.init() can "
        "initialize a different mixer format. This changes playback pitch and duration."),
      p("Tone generation now uses the active mixer sample rate and repeats each sample for "
        "the active channel count. Unsupported sample formats or initialization errors disable "
        "audio without stopping the game. Jump feedback is emitted only for an accepted, "
        "grounded jump, so repeated airborne key presses no longer produce a false sound."),
      p("The tests verify generated durations with dummy audio and the no-device fallback. "
        "A physical speaker/headphone check remains outside this automated run.", "Note")]
s += page("4. Testing, reproduction and reflection")
s += [table([["Check", "Cases", "Result"],
             ["Fast falling, no horizontal overlap, rising through platform", "3", "Pass"],
             ["Goal scoring and reset; hazard death", "2", "Pass"],
             ["Restart: Easy, Medium, Hard, unknown fallback", "4", "Pass"],
             ["Below-screen death and frozen state", "1", "Pass"],
             ["Grounded jump sound; tone duration; missing audio device", "3", "Pass"],
             ["Total", "13", "13 passed; exit code 0"]], [327, 45, 127]),
      Spacer(1, 10), p("The original five tests passed before this review, but the restart test "
        "replaced restart with a lambda and merely asserted the unchanged score. Passing that "
        "test did not verify replay. The revised test calls the real method and checks state "
        "and physics settings. Full pytest output is saved in evidence/tests.txt. One upstream "
        "Pygame pkg_resources deprecation warning remains; it does not fail the suite."),
      p("Reproduce from the repository root", "Heading2"),
      Preformatted("python -m pip install -r requirements-dev.txt\npython -m pytest test_game.py -v\npython tools/capture_evidence.py\npython tools/build_report.py\npython main.py", styles["ReportCode"]),
      p("LLM-assisted review and learning", "Heading2"),
      p("For this report session, the assistant inspected source and Git history, identified "
        "the ineffective replay test and audio issues, made focused changes, ran regression "
        "checks and generated evidence. The technical review distinguishes a passing assertion "
        "from a useful behavioral test, and a generated sound buffer from verified physical "
        "playback. This report summarizes the session; it does not reconstruct the complete "
        "LLM conversations used for the earlier task commits."),
      p("Submission status and remaining evidence", "Heading2"),
      p("The repository README lists two 10-second gameplay videos (before and after changes) "
        "and a complete Chat/LLM page link as submission items. No such videos or shareable "
        "chat link were present in the reviewed tree. The still images and controlled "
        "experiment in this PDF supplement that evidence; they do not replace those items."),
      p("References", "Heading2"),
      p('1. <link href="https://github.com/SunOrangeBurger/44_simple-platformer/blob/main/README.md" '
        'color="#087f8c">Repository README: tasks, expected behavior and submission checklist</link>.<br/>'
        '2. Repository source: main.py, game/game_engine.py, game/player.py, game/platform.py, '
        'game/hazard.py and test_game.py.<br/>'
        '3. Git starter 140ee4d and task commits listed on page 3.<br/>'
        '4. evidence/collision_comparison.txt, evidence/tests.txt and generated Pygame images.', "Note")]
SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=48, rightMargin=48,
                  topMargin=44, bottomMargin=54, title="Lab 4 - Simple Platformer",
                  author="Arun Hariharan").build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)


