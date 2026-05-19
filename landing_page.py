import streamlit as st
import streamlit.components.v1 as components

# ⚙️ Στήσιμο Σελίδας Streamlit
st.set_page_config(page_title="does4u - Premium Agency", page_icon="🎯", layout="wide")

# 🎨 Το HTML & CSS (Tailwind) για το Landing Page
landing_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
        .gradient-bg {
            background: radial-gradient(circle at 10% 20%, rgba(243, 246, 249, 1) 0%, rgba(255, 255, 255, 1) 90%);
        }
        .tech-line {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        }
    </style>
</head>
<body class="gradient-bg text-slate-800">

    <nav class="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="bg-blue-900 text-white p-2.5 rounded-xl shadow-md shadow-blue-900/20">
                <i class="fa-solid fa-gauge-high text-xl"></i>
            </div>
            <span class="text-2xl font-bold tracking-tight text-slate-900">does<span class="text-blue-600">4u</span></span>
        </div>
        <div class="hidden md:flex space-x-8 font-medium text-slate-600">
            <a href="#about" class="hover:text-blue-600 transition">About</a>
            <a href="#services" class="hover:text-blue-600 transition">Services</a>
            <a href="#contact" class="hover:text-blue-600 transition">Contact</a>
        </div>
        <a href="#contact" class="bg-slate-900 hover:bg-blue-900 text-white px-5 py-2.5 rounded-xl font-medium transition shadow-sm">
            Get a Free Quote
        </a>
    </nav>

    <header class="max-w-7xl mx-auto px-6 pt-16 pb-24 grid md:grid-cols-12 gap-12 items-center relative overflow-hidden">
        <div class="md:col-span-7 space-y-6 z-10">
            <div class="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold tracking-wide uppercase">
                <span class="w-2 h-2 rounded-full bg-blue-600 animate-pulse"></span>
                <span>Available for New Projects</span>
            </div>
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
                Unlock Efficiency.<br>Elevate Growth.
            </h1>
            <p class="text-xl font-bold text-slate-900 max-w-xl leading-relaxed">
                Your Strategic Partner for Scalable SaaS Engineering and AI-Driven Automations.
            </p>
            <p class="text-slate-500 text-base max-w-lg">
                We build tailored digital solutions for forward-thinking businesses. Stop wasting hours on manual tasks.
            </p>
            <div class="pt-4">
                <a href="#contact" class="bg-blue-900 hover:bg-blue-800 text-white text-base font-semibold px-8 py-4 rounded-xl shadow-lg shadow-blue-900/20 transition inline-block">
                    Start Your Transformation
                </a>
            </div>
        </div>
        
        <div class="md:col-span-5 hidden md:block relative">
            <div class="absolute -top-20 -right-20 w-96 h-96 bg-blue-100 rounded-full blur-3xl opacity-50 z-0"></div>
            <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80" 
                 class="rounded-3xl shadow-2xl border border-white/50 z-10 relative" alt="Dashboard Technical View">
        </div>
    </header>

    <section id="services" class="max-w-7xl mx-auto px-6 py-20 border-t border-slate-200">
        <div class="text-center max-w-3xl mx-auto mb-16">
            <span class="text-blue-600 font-bold uppercase tracking-wider text-sm">Services</span>
            <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mt-2">Our Specialized Expertise</h2>
            <p class="text-slate-500 mt-3 text-lg">We build tailored digital solutions for forward-thinking businesses.</p>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <div class="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 group hover:-translate-y-1">
                <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <i class="fa-solid fa-cloud"></i>
                </div>
                <h3 class="text-lg font-bold text-slate-950 mb-2">SaaS Engineering</h3>
                <p class="text-sm font-semibold text-slate-700 mb-3">Building Scalable, Robust, Secure Platforms</p>
                <p class="text-slate-400 text-xs leading-relaxed">Complete Development Lifecycle, Cloud Integration, Performance Optimization.</p>
            </div>

            <div class="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 group hover:-translate-y-1">
                <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <i class="fa-solid fa-network-wired"></i>
                </div>
                <h3 class="text-lg font-bold text-slate-950 mb-2">AI Automations</h3>
                <p class="text-sm font-semibold text-slate-700 mb-3">Streamline Operations & Decision Making</p>
                <p class="text-slate-400 text-xs leading-relaxed">Machine Learning, Workflow Automation, Data-Driven Insights, Conversational AI.</p>
            </div>

            <div class="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 group hover:-translate-y-1">
                <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <i class="fa-solid fa-spider"></i>
                </div>
                <h3 class="text-lg font-bold text-slate-950 mb-2">Web Scraping</h3>
                <p class="text-sm font-semibold text-slate-700 mb-3">Data Acquisition from Across the Web</p>
                <p class="text-slate-400 text-xs leading-relaxed">Scalable Data Extraction, Competitor Intelligence, Market Research, API Building.</p>
            </div>

            <div class="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 group hover:-translate-y-1">
                <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <i class="fa-brands fa-python"></i>
                </div>
                <h3 class="text-lg font-bold text-slate-950 mb-2">Python Scripts</h3>
                <p class="text-sm font-semibold text-slate-700 mb-3">Automate Any Task, Simplify Workflows</p>
                <p class="text-slate-400 text-xs leading-relaxed">Custom Scripting, Data Analysis, System Automation, Rapid Prototyping.</p>
            </div>
        </div>
    </section>

    <section id="contact" class="bg-slate-900 text-white py-20 rounded-t-[2.5rem]">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h2 class="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">Ready to Transform Your Business?</h2>
            <p class="text-slate-400 text-lg mb-10 max-w-xl mx-auto">Get in touch today for a free evaluation of your workflow automations.</p>
            
            <form class="bg-white p-8 rounded-2xl shadow-xl text-left max-w-lg mx-auto space-y-4 text-slate-800">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Your Name</label>
                    <input type="text" placeholder="John Doe" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 bg-slate-50">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Professional Email</label>
                    <input type="email" placeholder="john@company.com" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 bg-slate-50">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-1">Message</label>
                    <textarea rows="3" placeholder="Tell us about your automation needs..." class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 bg-slate-50"></textarea>
                </div>
                <button type="button" class="w-full bg-blue-900 hover:bg-blue-800 text-white font-bold py-3.5 rounded-xl transition shadow-lg shadow-blue-900/10">
                    Contact Us Today
                </button>
            </form>
        </div>
    </section>

    <footer class="bg-slate-950 text-slate-500 py-8 text-center text-sm border-t border-slate-900">
        <p>&copy; 2026 does4u. All Rights Reserved.</p>
    </footer>

</body>
</html>
"""

# ✨ Εμφάνιση του Landing Page μέσα στο Streamlit
components.html(landing_html, height=1400, scroller=True)