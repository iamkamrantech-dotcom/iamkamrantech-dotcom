# Animated GitHub Profile — Poori Guide (Roman Urdu)

Yeh guide tumhein zero se le kar chalte hue animated GitHub profile tak le jaayegi.
Har command copy-paste karne ke liye tayyar hai. Jaldi mat karo, ek ek step karo.

---

## Pehle samjho: yeh kaam karta kaise hai?

GitHub README me **JavaScript nahi chalta** aur **CSS bhi block ho jaati hai**.
Lekin GitHub `<img>` ke zariye lagayi hui **SVG file ke andar ki animation chala deta hai**.

Isi liye trick yeh hai:
- Saari animation SVG file ke **andar** rakho
- README sirf 3 SVG images ko jagah par lagata hai

Teen files banengi:

| File | Kya hai | Kab update hoti hai |
|---|---|---|
| `avi-ascii.svg` | Tumhari photo ka ASCII portrait (type hota hua) | Jab photo change karo |
| `info-card.svg` | Neofetch jaisa info panel | Jab details change karo |
| `contrib-heatmap.svg` | Tumhara asli contribution graph | **Roz apne aap** (GitHub Actions) |

---

## Step 0 — Zaroori cheezein install karo

Apne computer par yeh hone chahiye:

1. **Git** — https://git-scm.com/downloads
2. **Python 3.10+** — https://python.org/downloads
   (Windows par install karte waqt **"Add Python to PATH"** ka checkbox zaroor tick karo)
3. Ek **GitHub account**

Check karne ke liye terminal / CMD kholo aur likho:

```bash
git --version
python --version      # Mac/Linux par: python3 --version
```

Dono ka version number aa jaye to sab theek hai.

---

## Step 1 — "Magic" repository banao

GitHub ek khaas repo deta hai: **jis ka naam bilkul tumhara username ho**.
Us repo ka README tumhare profile page ke upar dikhta hai.

1. https://github.com/new par jao
2. **Repository name** me bilkul apna username likho (agar username `ali-khan` hai to repo ka naam bhi `ali-khan`)
3. **Public** select karo
4. **Add a README file** par tick karo
5. **Create repository** dabao

GitHub tumhein green box me batayega ke "you found a secret" — matlab sahi repo ban gaya.

Ab ise apne computer par laao:

```bash
git clone https://github.com/TUMHARA-USERNAME/TUMHARA-USERNAME.git
cd TUMHARA-USERNAME
```

---

## Step 2 — Files apni jagah par rakho

Is folder ka structure aisa hona chahiye:

```
TUMHARA-USERNAME/
├── README.md
├── scripts/
│   ├── fetch_contributions.py
│   ├── render_heatmap_svg.py
│   ├── make_ascii_svg.py
│   ├── make_info_card.py
│   └── requirements.txt
├── data/
└── .github/
    └── workflows/
        └── update-profile-art.yml
```

Jo zip main ne di hai, us ke andar sab kuch isi tarteeb me hai — bas sab kuch
apne cloned folder me copy kar do.

Agar folders khud banana ho:

```bash
mkdir -p scripts data .github/workflows
```

---

## Step 3 — Python packages install karo

```bash
# virtual environment (safai ke liye — optional lekin behtar)
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac / Linux:
source .venv/bin/activate

# heatmap ke liye (zaroori)
pip install requests beautifulsoup4

# ASCII portrait ke liye (sirf apne computer par)
pip install pillow numpy opencv-python-headless
```

> `rembg` optional hai (background khud hata deta hai). Agar install karna ho:
> `pip install rembg` — thoda bhaari hai (~200MB). Na ho to bhi script chal jaayegi,
> bas saaf/plain background wali photo use karna.

---

## Step 4 — Contribution heatmap banao (sab se maza yahi hai)

### 4a. Apna username set karo

`scripts/fetch_contributions.py` kholo, upar yeh line hai:

```python
USERNAME = "AVIVASHISHTA29"
```

Ise apne username se badal do:

```python
USERNAME = "TUMHARA-USERNAME"
```

### 4b. Data fetch karo

```bash
python scripts/fetch_contributions.py
```

Output aisa aayega:

```
[*] Fetching contributions for @tumhara-username ...
[+] 370 din save hue -> data/contributions.json
    total=1234  current_streak=5  longest_streak=41
```

> **Note:** koi token / API key nahi chahiye. Yeh GitHub ka public page parhta hai.

### 4c. SVG banao

```bash
python scripts/render_heatmap_svg.py
```

`contrib-heatmap.svg` ban jaayegi. Ise browser me kholo (double-click karo) —
boxes diagonal wave ki tarah aate hue dikhne chahiye.

---

## Step 5 — ASCII portrait banao

### 5a. Photo tayyar karo

Achhi photo ke liye:
- Chehra saaf dikhe, seedha camera ki taraf
- **Background jitna plain ho utna behtar** (safed deewar sab se best)
- Roshni ek taraf se aa rahi ho (bilkul flat light se portrait dhabba lagta hai)

Photo ko repo folder me `source-photo.jpg` naam se rakh do.

### 5b. Convert karo

```bash
python scripts/make_ascii_svg.py source-photo.jpg
```

`avi-ascii.svg` ban jaayegi.

### 5c. Tweak karo agar theek na lage

| Problem | Solution |
|---|---|
| Bohot ghana / kaala lag raha hai | `--cols 80 --rows 42` (kam detail) |
| Ulta lag raha hai (dark photo thi) | `--invert` lagao |
| Background bhi print ho gaya | `pip install rembg` phir dobara chalao |
| Typing bohot slow hai | `--stagger 0.02` |

Misal:

```bash
python scripts/make_ascii_svg.py source-photo.jpg --cols 90 --rows 48 --stagger 0.03
```

---

## Step 6 — Info card banao

`scripts/make_info_card.py` kholo. Upar `CONFIG` section hai:

```python
USERNAME = "avi"
HOST = "github"

ROWS = [
    ("Now",   "Full-Stack Developer @ Somewhere"),
    ("Stack", "Python · TypeScript · React · Docker"),
    ...
]
```

Ise apni details se badal do. Rows kam ya ziada bhi kar sakte ho.

```bash
python scripts/make_info_card.py
```

`info-card.svg` ban jaayegi.

> Preview ke liye bina animation wali version: `STATIC=1 python scripts/make_info_card.py`
> (Windows CMD par: `set STATIC=1` phir command chalao)

---

## Step 7 — README lagao

`README.md` kholo aur ye 3 cheezein badlo:

1. `avi@github` ko apne naam se badlo (3 jagah hai)
2. LinkedIn / X ke links me `USERNAME` badlo
3. Email badlo

**Width ka hisaab yaad rakhna:** heatmap `860` = portrait `370` + card `490`.
Agar ek badlo to doosre bhi adjust karo, warna kinare match nahi karenge.

### GitHub README ke 3 traps (yaad rakho):

1. `style="margin-top:20px"` **kaam nahi karega** — GitHub inline CSS hata deta hai.
   Spacing ke liye sirf `<br>` chalta hai.
2. `<h1>` aur `<h2>` ke neeche poori chaurai ki line aa jaati hai. Title ke liye
   `<h3>` use karo.
3. Do images ko ek line me rakhne ka **sirf `<table>`** hi reliable tareeqa hai.

---

## Step 8 — GitHub par push karo

```bash
git add .
git commit -m "feat: animated profile readme"
git push
```

Ab `https://github.com/TUMHARA-USERNAME` kholo — sab kuch chalta hua dikhna chahiye.

> Agar animation na chale: page hard-refresh karo (Ctrl+Shift+R).
> GitHub images ko cache karta hai, thoda time lag sakta hai.

---

## Step 9 — Roz auto-update karwao

`.github/workflows/update-profile-art.yml` file pehle se tayyar hai. Yeh roz
subah heatmap dobara banata hai aur khud commit kar deta hai.

Ek dafa manually test karo:

1. Apne repo me **Actions** tab par jao
2. Left side se **"Update profile art"** chuno
3. Right side **"Run workflow"** > **Run workflow** dabao
4. 1-2 minute baad green tick aana chahiye aur ek naya commit dikhega

**Agar permission error aaye:**
Settings > Actions > General > neeche "Workflow permissions" me
**"Read and write permissions"** select karo aur Save dabao.

---

## Aam masail (Troubleshooting)

| Error | Wajah / Hal |
|---|---|
| `Username nahi mila (404)` | `USERNAME` galat likha hai |
| `data/contributions.json nahi mila` | Pehle `fetch_contributions.py` chalao |
| `ModuleNotFoundError: requests` | `pip install requests beautifulsoup4` |
| README par images tootin hui | Path `./file.svg` hona chahiye, aur file push hui ho |
| Profile par README dikh hi nahi raha | Repo ka naam **bilkul** username jaisa nahi hai, ya repo private hai |
| Actions commit nahi kar raha | Workflow permissions "Read and write" karo (Step 9) |

---

## Roz ka kaam kya hai?

Kuch bhi nahi. Heatmap khud update hota rahega.
Sirf tab kuch karna hai jab:

- **Photo badalni ho** → `make_ascii_svg.py` dobara chalao, push karo
- **Details badalni hon** → `make_info_card.py` me CONFIG edit karo, chalao, push karo

Bas. Enjoy karo. 🚀
