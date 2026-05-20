"""
Generates the Viraj Junction water park website (Kagal, Maharashtra).
Run: python generate_website.py
Output: ./viraj_junction/ directory with all HTML/CSS files.
"""

import os

OUTPUT_DIR = "viraj_junction"

PAGES = ["index", "about", "attractions", "contact"]

COLORS = {
    "primary": "#0077b6",
    "secondary": "#00b4d8",
    "accent": "#90e0ef",
    "dark": "#03045e",
    "light": "#caf0f8",
    "white": "#ffffff",
    "text": "#1a1a2e",
}

NAV_LINKS = [
    ("Home", "index.html"),
    ("About", "about.html"),
    ("Attractions", "attractions.html"),
    ("Contact", "contact.html"),
]


def nav_html(active_page):
    links = ""
    for label, href in NAV_LINKS:
        active_class = ' class="active"' if href == f"{active_page}.html" else ""
        links += f'<li><a href="{href}"{active_class}>{label}</a></li>\n'
    return f"""
    <nav class="navbar">
      <div class="nav-brand">
        <span class="drop">&#9730;</span> Viraj Junction
      </div>
      <ul class="nav-links">
        {links}
      </ul>
    </nav>"""


def footer_html():
    return """
    <footer>
      <div class="footer-content">
        <div class="footer-col">
          <h3>&#9730; Viraj Junction</h3>
          <p>The ultimate water park experience in Kagal, Maharashtra.</p>
        </div>
        <div class="footer-col">
          <h3>Quick Links</h3>
          <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="about.html">About Us</a></li>
            <li><a href="attractions.html">Attractions</a></li>
            <li><a href="contact.html">Contact</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Contact</h3>
          <p>Kagal, Kolhapur District<br>Maharashtra, India</p>
          <p>Phone: +91 98765 43210</p>
          <p>Email: info@virajjunction.com</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 Viraj Junction Water Park. All rights reserved.</p>
      </div>
    </footer>"""


def base_html(title, active_page, body_content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Viraj Junction Water Park</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  {nav_html(active_page)}
  <main>
    {body_content}
  </main>
  {footer_html()}
</body>
</html>"""


def page_index():
    body = """
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome to Viraj Junction</h1>
        <p class="tagline">Kagal's Premier Water Park Experience</p>
        <p>Dive into a world of thrills, splashes, and unforgettable memories<br>
           in the heart of Kagal, Kolhapur District, Maharashtra.</p>
        <div class="hero-buttons">
          <a href="attractions.html" class="btn btn-primary">Explore Rides</a>
          <a href="contact.html" class="btn btn-outline">Plan Your Visit</a>
        </div>
      </div>
    </section>

    <section class="highlights">
      <h2>Why Choose Viraj Junction?</h2>
      <div class="card-grid">
        <div class="card">
          <div class="card-icon">&#127946;</div>
          <h3>Thrilling Rides</h3>
          <p>Over 20 exciting water rides and slides for all ages.</p>
        </div>
        <div class="card">
          <div class="card-icon">&#127775;</div>
          <h3>Safe &amp; Clean</h3>
          <p>Internationally maintained safety and hygiene standards.</p>
        </div>
        <div class="card">
          <div class="card-icon">&#127860;</div>
          <h3>Food &amp; Drinks</h3>
          <p>Multiple restaurants and snack counters inside the park.</p>
        </div>
        <div class="card">
          <div class="card-icon">&#127968;</div>
          <h3>Family Friendly</h3>
          <p>Dedicated kids' zones and wave pools for the whole family.</p>
        </div>
      </div>
    </section>

    <section class="timings-banner">
      <h2>Park Timings &amp; Entry</h2>
      <div class="timings-grid">
        <div class="timing-item">
          <span class="timing-label">Open Days</span>
          <span class="timing-value">Monday – Sunday</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Hours</span>
          <span class="timing-value">10:00 AM – 6:00 PM</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Adult Ticket</span>
          <span class="timing-value">&#8377; 599</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Child Ticket</span>
          <span class="timing-value">&#8377; 399</span>
        </div>
      </div>
    </section>"""
    return base_html("Home", "index", body)


def page_about():
    body = """
    <section class="page-hero">
      <h1>About Viraj Junction</h1>
      <p>Our story, our mission, and our commitment to fun.</p>
    </section>

    <section class="about-section">
      <div class="about-text">
        <h2>Who We Are</h2>
        <p>Viraj Junction Water Park is Kagal's most loved destination for water-based
           entertainment. Nestled in the culturally rich Kolhapur District of Maharashtra,
           we bring world-class water park experiences to the heart of Western Maharashtra.</p>
        <p>Founded with a vision to create a safe, joyful, and memorable space for families,
           couples, and groups of all kinds, Viraj Junction has grown to become a landmark
           attraction in the region.</p>
        <h2>Our Mission</h2>
        <p>To deliver unmatched fun, safety, and hospitality to every guest who walks through
           our gates — making each visit a memory that lasts a lifetime.</p>
      </div>
      <div class="about-stats">
        <div class="stat-card">
          <span class="stat-num">20+</span>
          <span class="stat-label">Water Rides</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">5</span>
          <span class="stat-label">Restaurants</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">10K+</span>
          <span class="stat-label">Happy Visitors/Year</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">100%</span>
          <span class="stat-label">Safety Certified</span>
        </div>
      </div>
    </section>

    <section class="location-section">
      <h2>Our Location</h2>
      <p>We are conveniently located in <strong>Kagal, Kolhapur District, Maharashtra</strong>
         — easily accessible from Kolhapur city (approx. 20 km) and well connected by road.</p>
      <div class="location-details">
        <div class="location-item">&#128205; Kagal, Kolhapur, Maharashtra 416236</div>
        <div class="location-item">&#128664; 20 km from Kolhapur city centre</div>
        <div class="location-item">&#128652; Regular buses from Kolhapur Bus Stand</div>
        <div class="location-item">&#128663; Ample free parking available</div>
      </div>
    </section>"""
    return base_html("About Us", "about", body)


def page_attractions():
    rides = [
        ("Wave Pool", "&#127754;", "Experience the thrill of ocean waves in our massive wave pool — great for all age groups."),
        ("Tornado Slide", "&#127744;", "A high-speed spiral slide that sends you into a splash pool at the bottom."),
        ("Lazy River", "&#128695;", "Float along our 300-metre lazy river on an inflatable ring — pure relaxation."),
        ("Family Raft Ride", "&#9975;", "A group ride on a giant raft through twists and turns — perfect for families."),
        ("Kids' Splash Zone", "&#128231;", "A dedicated safe zone for little ones with mini slides, water sprays, and splash pads."),
        ("Kamikaze Slide", "&#9889;", "Our steepest drop slide — not for the faint-hearted! 15 metres of pure adrenaline."),
        ("Rain Dance", "&#127783;", "Open-air dance floor with overhead rain showers and music — a crowd favourite."),
        ("Speed Slides", "&#128230;", "Three parallel speed slides — race your friends to the bottom!"),
    ]

    cards = ""
    for name, icon, desc in rides:
        cards += f"""
        <div class="card">
          <div class="card-icon">{icon}</div>
          <h3>{name}</h3>
          <p>{desc}</p>
        </div>"""

    body = f"""
    <section class="page-hero">
      <h1>Our Attractions</h1>
      <p>Over 20 thrilling rides and zones for every kind of visitor.</p>
    </section>

    <section class="attractions-section">
      <div class="card-grid">
        {cards}
      </div>
    </section>

    <section class="timings-banner">
      <h2>Ticket Prices</h2>
      <div class="timings-grid">
        <div class="timing-item">
          <span class="timing-label">Adult (12+ years)</span>
          <span class="timing-value">&#8377; 599</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Child (3–11 years)</span>
          <span class="timing-value">&#8377; 399</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Senior (60+)</span>
          <span class="timing-value">&#8377; 299</span>
        </div>
        <div class="timing-item">
          <span class="timing-label">Group (20+ pax)</span>
          <span class="timing-value">10% off</span>
        </div>
      </div>
    </section>"""
    return base_html("Attractions", "attractions", body)


def page_contact():
    body = """
    <section class="page-hero">
      <h1>Contact Us</h1>
      <p>We'd love to hear from you. Plan your visit or ask us anything!</p>
    </section>

    <section class="contact-section">
      <div class="contact-info">
        <h2>Get in Touch</h2>
        <div class="contact-item">
          <span class="contact-icon">&#128205;</span>
          <div>
            <strong>Address</strong><br>
            Viraj Junction Water Park,<br>
            Kagal, Kolhapur District,<br>
            Maharashtra – 416236, India
          </div>
        </div>
        <div class="contact-item">
          <span class="contact-icon">&#128222;</span>
          <div>
            <strong>Phone</strong><br>
            +91 98765 43210<br>
            +91 91234 56789
          </div>
        </div>
        <div class="contact-item">
          <span class="contact-icon">&#128140;</span>
          <div>
            <strong>Email</strong><br>
            info@virajjunction.com<br>
            bookings@virajjunction.com
          </div>
        </div>
        <div class="contact-item">
          <span class="contact-icon">&#128336;</span>
          <div>
            <strong>Park Hours</strong><br>
            Monday – Sunday<br>
            10:00 AM – 6:00 PM
          </div>
        </div>
      </div>

      <div class="contact-form">
        <h2>Send a Message</h2>
        <form>
          <div class="form-group">
            <label for="name">Your Name</label>
            <input type="text" id="name" name="name" placeholder="Enter your name" required />
          </div>
          <div class="form-group">
            <label for="email">Email Address</label>
            <input type="email" id="email" name="email" placeholder="Enter your email" required />
          </div>
          <div class="form-group">
            <label for="phone">Phone Number</label>
            <input type="tel" id="phone" name="phone" placeholder="+91 00000 00000" />
          </div>
          <div class="form-group">
            <label for="message">Message</label>
            <textarea id="message" name="message" rows="5"
                      placeholder="Tell us about your visit plans or ask a question..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Send Message</button>
        </form>
      </div>
    </section>"""
    return base_html("Contact", "contact", body)


def css():
    return f"""/* Viraj Junction Water Park — Stylesheet */

*, *::before, *::after {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

:root {{
  --primary:   {COLORS['primary']};
  --secondary: {COLORS['secondary']};
  --accent:    {COLORS['accent']};
  --dark:      {COLORS['dark']};
  --light:     {COLORS['light']};
  --white:     {COLORS['white']};
  --text:      {COLORS['text']};
}}

body {{
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text);
  background: var(--white);
  line-height: 1.6;
}}

/* ── Navbar ── */
.navbar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--dark);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}}

.nav-brand {{
  color: var(--white);
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 1px;
}}

.nav-brand .drop {{
  color: var(--accent);
}}

.nav-links {{
  list-style: none;
  display: flex;
  gap: 2rem;
}}

.nav-links a {{
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}}

.nav-links a:hover,
.nav-links a.active {{
  color: var(--white);
}}

/* ── Hero ── */
.hero {{
  background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 60%, var(--secondary) 100%);
  color: var(--white);
  text-align: center;
  padding: 6rem 2rem;
}}

.hero h1 {{
  font-size: 3rem;
  margin-bottom: 0.5rem;
}}

.tagline {{
  font-size: 1.3rem;
  color: var(--accent);
  margin-bottom: 1rem;
  font-style: italic;
}}

.hero p {{
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}}

.hero-buttons {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}

/* ── Page Hero (inner pages) ── */
.page-hero {{
  background: linear-gradient(135deg, var(--dark), var(--primary));
  color: var(--white);
  text-align: center;
  padding: 4rem 2rem;
}}

.page-hero h1 {{
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}}

.page-hero p {{
  font-size: 1.1rem;
  opacity: 0.85;
}}

/* ── Buttons ── */
.btn {{
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}}

.btn:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}}

.btn-primary {{
  background: var(--secondary);
  color: var(--white);
}}

.btn-outline {{
  border-color: var(--white);
  color: var(--white);
  background: transparent;
}}

.btn-outline:hover {{
  background: var(--white);
  color: var(--dark);
}}

/* ── Sections ── */
section {{
  padding: 4rem 2rem;
}}

section h2 {{
  text-align: center;
  font-size: 2rem;
  color: var(--primary);
  margin-bottom: 2rem;
}}

/* ── Card Grid ── */
.card-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  max-width: 1100px;
  margin: 0 auto;
}}

.card {{
  background: var(--light);
  border-radius: 12px;
  padding: 2rem 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}}

.card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,119,182,0.15);
}}

.card-icon {{
  font-size: 2.5rem;
  margin-bottom: 1rem;
}}

.card h3 {{
  color: var(--primary);
  margin-bottom: 0.5rem;
}}

/* ── Timings Banner ── */
.timings-banner {{
  background: var(--primary);
  color: var(--white);
}}

.timings-banner h2 {{
  color: var(--accent);
}}

.timings-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}}

.timing-item {{
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}}

.timing-label {{
  font-size: 0.9rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

.timing-value {{
  font-size: 1.4rem;
  font-weight: 700;
}}

/* ── About Page ── */
.about-section {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  max-width: 1100px;
  margin: 0 auto;
  align-items: start;
}}

.about-text h2 {{
  text-align: left;
  margin-top: 1.5rem;
  font-size: 1.5rem;
}}

.about-text p {{
  margin-bottom: 1rem;
}}

.about-stats {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}}

.stat-card {{
  background: var(--light);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}}

.stat-num {{
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}}

.stat-label {{
  font-size: 0.9rem;
  color: var(--text);
  opacity: 0.75;
}}

.location-section {{
  background: var(--light);
  border-radius: 16px;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}}

.location-details {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}}

.location-item {{
  font-size: 1rem;
}}

/* ── Attractions ── */
.attractions-section {{
  max-width: 1100px;
  margin: 0 auto;
}}

/* ── Contact Page ── */
.contact-section {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  max-width: 1100px;
  margin: 0 auto;
  align-items: start;
}}

.contact-section h2 {{
  text-align: left;
  margin-bottom: 1.5rem;
}}

.contact-item {{
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
}}

.contact-icon {{
  font-size: 1.5rem;
}}

.form-group {{
  margin-bottom: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}}

.form-group label {{
  font-weight: 600;
  font-size: 0.95rem;
}}

.form-group input,
.form-group textarea {{
  padding: 0.75rem 1rem;
  border: 1.5px solid var(--accent);
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
  resize: vertical;
}}

.form-group input:focus,
.form-group textarea:focus {{
  outline: none;
  border-color: var(--primary);
}}

/* ── Footer ── */
footer {{
  background: var(--dark);
  color: var(--white);
  padding: 3rem 2rem 1rem;
}}

.footer-content {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}}

footer h3 {{
  color: var(--accent);
  margin-bottom: 1rem;
}}

footer p,
footer li {{
  opacity: 0.8;
  font-size: 0.95rem;
  margin-bottom: 0.4rem;
}}

footer ul {{
  list-style: none;
}}

footer a {{
  color: var(--accent);
  text-decoration: none;
}}

footer a:hover {{
  color: var(--white);
}}

.footer-bottom {{
  text-align: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 0.85rem;
  opacity: 0.6;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .hero h1 {{ font-size: 2rem; }}
  .about-section,
  .contact-section {{ grid-template-columns: 1fr; }}
  .about-stats {{ grid-template-columns: 1fr 1fr; }}
  .nav-links {{ gap: 1rem; }}
}}

@media (max-width: 480px) {{
  .navbar {{ flex-direction: column; gap: 0.75rem; }}
  .nav-links {{ flex-wrap: wrap; justify-content: center; }}
  .hero h1 {{ font-size: 1.6rem; }}
}}
"""


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pages = {
        "index": page_index(),
        "about": page_about(),
        "attractions": page_attractions(),
        "contact": page_contact(),
    }

    for name, html in pages.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Created: {path}")

    css_path = os.path.join(OUTPUT_DIR, "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css())
    print(f"  Created: {css_path}")

    print(f"\nWebsite generated in '{OUTPUT_DIR}/'")
    print("Open viraj_junction/index.html in a browser to preview.")


if __name__ == "__main__":
    generate()
