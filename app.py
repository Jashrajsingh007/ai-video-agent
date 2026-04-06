from flask import Flask, request, jsonify, render_template_string
from agent import run_agent
from tools import get_tasks, get_calendar_events, get_notes

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CreatorOS - AI Video Production Suite</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #000; color: #fff; overflow-x: hidden; }

        /* INTRO */
        #intro {
            position: fixed; inset: 0; background: #000;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            z-index: 1000; transition: opacity 0.8s ease, transform 0.8s ease;
        }
        #intro.hide { opacity: 0; transform: scale(1.1); pointer-events: none; }
        .globe-wrap { position: relative; width: 200px; height: 200px; margin-bottom: 40px; }
        .globe {
            width: 200px; height: 200px; border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #00d4ff44, #0044ff22, #000066);
            border: 1px solid #00d4ff44;
            animation: globePulse 3s ease-in-out infinite;
            box-shadow: 0 0 60px #00d4ff33, 0 0 120px #0044ff22, inset 0 0 60px #00d4ff11;
        }
        .orbit {
            position: absolute; border-radius: 50%;
            border: 1px solid #00d4ff33; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
        }
        .orbit-1 { width: 240px; height: 240px; animation: orbit1 4s linear infinite; }
        .orbit-2 { width: 280px; height: 140px; animation: orbit2 6s linear infinite; border-color: #0099ff22; }
        .orbit-3 { width: 320px; height: 100px; animation: orbit3 8s linear infinite; border-color: #00d4ff11; }
        .dot {
            position: absolute; width: 6px; height: 6px;
            background: #00d4ff; border-radius: 50%;
            box-shadow: 0 0 10px #00d4ff; top: -3px; left: 50%;
            transform: translateX(-50%);
        }
        @keyframes globePulse {
            0%, 100% { box-shadow: 0 0 60px #00d4ff33, inset 0 0 60px #00d4ff11; }
            50% { box-shadow: 0 0 100px #00d4ff55, inset 0 0 80px #00d4ff22; }
        }
        @keyframes orbit1 { from { transform: translate(-50%,-50%) rotate(0deg); } to { transform: translate(-50%,-50%) rotate(360deg); } }
        @keyframes orbit2 { from { transform: translate(-50%,-50%) rotateX(75deg) rotate(0deg); } to { transform: translate(-50%,-50%) rotateX(75deg) rotate(360deg); } }
        @keyframes orbit3 { from { transform: translate(-50%,-50%) rotateX(85deg) rotate(0deg); } to { transform: translate(-50%,-50%) rotateX(85deg) rotate(360deg); } }
        .intro-title { font-size: 52px; font-weight: 900; letter-spacing: -2px; animation: fadeUp 1s ease 0.5s both; }
        .intro-title span { color: #00d4ff; }
        .intro-sub { color: #555; font-size: 16px; margin-top: 12px; animation: fadeUp 1s ease 0.8s both; }
        .intro-bar { width: 200px; height: 2px; background: #111; border-radius: 2px; margin-top: 40px; overflow: hidden; animation: fadeUp 1s ease 1s both; }
        .intro-bar-fill { height: 100%; background: linear-gradient(90deg, #00d4ff, #0066ff); animation: barFill 2.5s ease 1.2s both; }
        @keyframes barFill { from { width: 0%; } to { width: 100%; } }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        /* APP */
        #app { opacity: 0; transition: opacity 0.8s ease; min-height: 100vh; }
        #app.show { opacity: 1; }

        nav {
            position: fixed; top: 0; left: 0; right: 0;
            padding: 20px 40px; display: flex; align-items: center; justify-content: space-between;
            background: linear-gradient(180deg, #000 0%, transparent 100%); z-index: 100;
        }
        .nav-logo { font-size: 22px; font-weight: 900; }
        .nav-logo span { color: #00d4ff; }
        .nav-right { display: flex; align-items: center; gap: 12px; }
        .nav-tag { background: #00d4ff11; border: 1px solid #00d4ff33; color: #00d4ff; padding: 6px 14px; border-radius: 50px; font-size: 12px; font-weight: 600; }
        .nav-history-btn { background: #111; border: 1px solid #222; color: #888; padding: 8px 18px; border-radius: 50px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif; }
        .nav-history-btn:hover { border-color: #00d4ff44; color: #00d4ff; }

        /* HERO */
        .hero {
            min-height: 100vh; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            text-align: center; padding: 100px 20px 60px;
            background: radial-gradient(ellipse at 50% 0%, #00d4ff0a 0%, transparent 70%);
        }
        .hero-badge { background: #00d4ff11; border: 1px solid #00d4ff33; color: #00d4ff; padding: 8px 20px; border-radius: 50px; font-size: 13px; font-weight: 600; margin-bottom: 30px; display: inline-block; }
        .hero h1 { font-size: clamp(40px, 7vw, 80px); font-weight: 900; letter-spacing: -3px; line-height: 1.05; margin-bottom: 20px; }
        .hero h1 .blue { color: #00d4ff; }
        .hero h1 .dim { color: #333; }
        .hero p { color: #666; font-size: 18px; max-width: 500px; line-height: 1.6; margin-bottom: 50px; }

        .agents { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 50px; }
        .agent-pill { background: #111; border: 1px solid #222; border-radius: 50px; padding: 8px 18px; font-size: 13px; color: #555; transition: all 0.3s ease; }
        .agent-pill.active { background: #00d4ff11; border-color: #00d4ff; color: #00d4ff; box-shadow: 0 0 20px #00d4ff22; }

        .input-section { width: 100%; max-width: 700px; }
        .input-wrap { background: #0d0d0d; border: 1px solid #222; border-radius: 20px; padding: 5px; transition: border-color 0.3s; }
        .input-wrap:focus-within { border-color: #00d4ff44; box-shadow: 0 0 30px #00d4ff11; }
        textarea { width: 100%; background: transparent; border: none; outline: none; color: #fff; font-size: 16px; font-family: 'Inter', sans-serif; padding: 20px 25px; resize: none; min-height: 80px; }
        textarea::placeholder { color: #333; }
        .input-footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px; border-top: 1px solid #1a1a1a; }
        .input-hint { color: #333; font-size: 13px; }
        .btn { background: linear-gradient(135deg, #00d4ff, #0066ff); border: none; border-radius: 12px; color: #000; font-size: 14px; font-weight: 700; padding: 12px 28px; cursor: pointer; transition: opacity 0.2s, transform 0.2s; }
        .btn:hover { opacity: 0.9; transform: scale(1.02); }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

        /* LOADING */
        #loading { display: none; padding: 80px 20px; max-width: 900px; margin: 0 auto; }
        .loading-inner { display: flex; gap: 40px; align-items: flex-start; }
        .loading-left { flex: 1; text-align: center; }
        .loading-orb {
            width: 70px; height: 70px; border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #00d4ff, #0044ff);
            margin: 0 auto 30px; animation: orbPulse 1.5s ease-in-out infinite;
            box-shadow: 0 0 40px #00d4ff55;
        }
        @keyframes orbPulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 40px #00d4ff55; }
            50% { transform: scale(1.15); box-shadow: 0 0 70px #00d4ff88; }
        }
        .load-thought {
            font-size: 20px; font-weight: 800; letter-spacing: -0.5px;
            color: #fff; min-height: 32px; margin-bottom: 10px;
            opacity: 0; transform: translateY(8px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        .load-thought.show { opacity: 1; transform: translateY(0); }
        .load-thought span { color: #00d4ff; }
        .load-sub { color: #333; font-size: 14px; margin-bottom: 50px; }
        .wf-track-wrap { margin-top: 20px; }
        .wf-bar-bg { height: 2px; background: #111; border-radius: 2px; overflow: hidden; margin-bottom: 20px; }
        .wf-bar-fill {
            height: 100%; width: 0%;
            background: linear-gradient(90deg, #00d4ff, #0066ff);
            border-radius: 2px; transition: width 6s ease;
            box-shadow: 0 0 10px #00d4ff;
        }
        .wf-agents-row { display: flex; justify-content: space-between; gap: 8px; }
        .wf-agent-item { flex: 1; text-align: center; opacity: 0.25; transition: opacity 0.4s; }
        .wf-agent-item.active { opacity: 1; }
        .wf-agent-icon {
            width: 42px; height: 42px; border-radius: 50%;
            background: #0d0d0d; border: 1px solid #222;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; margin: 0 auto 8px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .wf-agent-item.active .wf-agent-icon { border-color: #00d4ff; box-shadow: 0 0 16px #00d4ff44; }
        .wf-agent-label { font-size: 10px; color: #444; font-weight: 600; letter-spacing: 0.5px; }
        .wf-agent-item.active .wf-agent-label { color: #00d4ff; }
        .loading-right { flex: 1; display: flex; flex-direction: column; gap: 12px; }
        .sk-card { background: #080808; border: 1px solid #111; border-radius: 16px; padding: 20px; overflow: hidden; }
        .sk-line {
            background: linear-gradient(90deg, #111 25%, #1c1c1c 50%, #111 75%);
            background-size: 200% 100%;
            border-radius: 6px;
            animation: shimmer 1.8s infinite;
        }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

        /* RESULTS */
        .results { display: none; max-width: 800px; margin: 0 auto; padding: 0 20px 80px; }
        .result-header { text-align: center; margin-bottom: 40px; padding-top: 40px; }
        .result-header h2 { font-size: 36px; font-weight: 900; }
        .result-header h2 span { color: #00d4ff; }
        .comp-display { background: linear-gradient(135deg, #00d4ff11, #0066ff11); border: 1px solid #00d4ff33; border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 20px; }
        .comp-name { font-size: 32px; font-weight: 900; color: #00d4ff; margin-bottom: 10px; }
        .render-cmd { background: #0a0a0a; border: 1px solid #222; border-radius: 10px; padding: 12px 20px; font-family: monospace; color: #00ff88; font-size: 14px; cursor: pointer; display: inline-block; transition: border-color 0.2s; }
        .render-cmd:hover { border-color: #00ff88; }
        .card { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; padding: 30px; margin-bottom: 16px; transition: border-color 0.3s; }
        .card:hover { border-color: #00d4ff22; }
        .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
        .card-title { font-size: 12px; font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 2px; }
        .copy-btn { background: #1a1a1a; border: 1px solid #333; color: #888; padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 12px; transition: all 0.2s; }
        .copy-btn:hover { background: #00d4ff11; border-color: #00d4ff; color: #00d4ff; }
        .card pre { color: #aaa; font-family: 'Inter', sans-serif; font-size: 14px; line-height: 1.8; white-space: pre-wrap; word-wrap: break-word; }
        .new-btn { display: block; width: 100%; padding: 16px; background: transparent; border: 1px solid #222; border-radius: 14px; color: #555; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 10px; transition: all 0.2s; font-family: 'Inter', sans-serif; }
        .new-btn:hover { border-color: #00d4ff33; color: #00d4ff; }

        /* HISTORY PANEL */
        #historyPanel {
            display: none; position: fixed; inset: 0; background: #000; z-index: 200;
            overflow-y: auto; padding: 40px 20px 80px;
        }
        #historyPanel.show { display: block; }
        .history-header { max-width: 900px; margin: 0 auto 40px; display: flex; align-items: center; justify-content: space-between; }
        .history-header h2 { font-size: 32px; font-weight: 900; }
        .history-header h2 span { color: #00d4ff; }
        .close-btn { background: #111; border: 1px solid #222; color: #888; padding: 10px 20px; border-radius: 12px; cursor: pointer; font-size: 14px; font-weight: 600; font-family: 'Inter', sans-serif; transition: all 0.2s; }
        .close-btn:hover { border-color: #00d4ff33; color: #00d4ff; }
        .history-grid { max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
        .h-section { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 20px; padding: 24px; }
        .h-section-title { font-size: 11px; font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        .h-section-title span { color: #00d4ff; font-size: 16px; }
        .h-item { background: #111; border: 1px solid #1a1a1a; border-radius: 12px; padding: 14px; margin-bottom: 10px; }
        .h-item-title { font-size: 13px; font-weight: 600; color: #ddd; margin-bottom: 4px; }
        .h-item-sub { font-size: 12px; color: #555; }
        .h-empty { color: #333; font-size: 14px; text-align: center; padding: 20px 0; }
        .h-loading { color: #555; font-size: 14px; text-align: center; padding: 20px 0; }
        @media (max-width: 700px) {
            .history-grid { grid-template-columns: 1fr; }
            .loading-inner { flex-direction: column; }
            .loading-right { display: none; }
        }
    </style>
</head>
<body>

<!-- INTRO -->
<div id="intro">
    <div class="globe-wrap">
        <div class="orbit orbit-1"><div class="dot"></div></div>
        <div class="orbit orbit-2"><div class="dot"></div></div>
        <div class="orbit orbit-3"><div class="dot"></div></div>
        <div class="globe"></div>
    </div>
    <div class="intro-title">Creator<span>OS</span></div>
    <div class="intro-sub">AI Video Production Suite - Powered by Gemini</div>
    <div class="intro-bar"><div class="intro-bar-fill"></div></div>
</div>

<!-- HISTORY PANEL -->
<div id="historyPanel">
    <div class="history-header">
        <h2>Your <span>Workspace</span></h2>
        <button class="close-btn" onclick="closeHistory()">X Close</button>
    </div>
    <div class="history-grid">
        <div class="h-section">
            <div class="h-section-title"><span>checkmark</span> Tasks</div>
            <div id="tasksList"><div class="h-loading">Loading...</div></div>
        </div>
        <div class="h-section">
            <div class="h-section-title"><span>calendar</span> Calendar</div>
            <div id="calendarList"><div class="h-loading">Loading...</div></div>
        </div>
        <div class="h-section">
            <div class="h-section-title"><span>notes</span> Notes</div>
            <div id="notesList"><div class="h-loading">Loading...</div></div>
        </div>
    </div>
</div>

<!-- MAIN APP -->
<div id="app">
    <nav>
        <div class="nav-logo">Creator<span>OS</span></div>
        <div class="nav-right">
            <button class="nav-history-btn" onclick="openHistory()">My Workspace</button>
            <div class="nav-tag">Powered by Gemini + ADK</div>
        </div>
    </nav>

    <!-- HERO -->
    <div class="hero" id="heroSection">
        <div class="hero-badge">Multi-Agent AI System</div>
        <h1>
            Turn Any Idea Into<br>
            <span class="blue">Production-Ready</span><br>
            <span class="dim">Video Content</span>
        </h1>
        <p>6 AI agents working together to generate strategy, scripts, tasks & Remotion code instantly</p>
        <div class="agents">
            <div class="agent-pill" id="a1">Composition</div>
            <div class="agent-pill" id="a2">Strategy</div>
            <div class="agent-pill" id="a3">Script</div>
            <div class="agent-pill" id="a4">Remotion</div>
            <div class="agent-pill" id="a5">Tasks</div>
            <div class="agent-pill" id="a6">Calendar</div>
        </div>
        <div class="input-section">
            <div class="input-wrap">
                <textarea id="prompt" placeholder="Describe your video... e.g. 'Create a product launch video for my AI SaaS tool called TaskFlow'"></textarea>
                <div class="input-footer">
                    <span class="input-hint">Enter to generate - Shift+Enter for new line</span>
                    <button class="btn" onclick="generate()" id="btn">Generate</button>
                </div>
            </div>
        </div>
    </div>

    <!-- LOADING -->
    <div id="loading">
        <div class="loading-inner">
            <div class="loading-left">
                <div class="loading-orb"></div>
                <div class="load-thought show" id="loadThought">Thinking<span>...</span></div>
                <div class="load-sub" id="loadSub">Our agents are working on your video</div>
                <div class="wf-track-wrap">
                    <div class="wf-bar-bg"><div class="wf-bar-fill" id="wfBarFill"></div></div>
                    <div class="wf-agents-row">
                        <div class="wf-agent-item" id="la1"><div class="wf-agent-icon">1</div><div class="wf-agent-label">Composition</div></div>
                        <div class="wf-agent-item" id="la2"><div class="wf-agent-icon">2</div><div class="wf-agent-label">Strategy</div></div>
                        <div class="wf-agent-item" id="la3"><div class="wf-agent-icon">3</div><div class="wf-agent-label">Script</div></div>
                        <div class="wf-agent-item" id="la4"><div class="wf-agent-icon">4</div><div class="wf-agent-label">Remotion</div></div>
                        <div class="wf-agent-item" id="la5"><div class="wf-agent-icon">5</div><div class="wf-agent-label">Tasks</div></div>
                        <div class="wf-agent-item" id="la6"><div class="wf-agent-icon">6</div><div class="wf-agent-label">Calendar</div></div>
                    </div>
                </div>
            </div>
            <div class="loading-right">
                <div class="sk-card" style="text-align:center; padding: 24px 20px;">
                    <div class="sk-line" style="width:40%; height:10px; margin: 0 auto 14px;"></div>
                    <div class="sk-line" style="width:55%; height:24px; margin: 0 auto 12px;"></div>
                    <div class="sk-line" style="width:65%; height:12px; margin: 0 auto;"></div>
                </div>
                <div class="sk-card">
                    <div class="sk-line" style="width:30%; height:9px; margin-bottom:16px;"></div>
                    <div class="sk-line" style="width:100%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:88%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:75%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:60%; height:9px;"></div>
                </div>
                <div class="sk-card">
                    <div class="sk-line" style="width:25%; height:9px; margin-bottom:16px;"></div>
                    <div class="sk-line" style="width:100%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:92%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:80%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:70%; height:9px;"></div>
                </div>
                <div class="sk-card">
                    <div class="sk-line" style="width:35%; height:9px; margin-bottom:16px;"></div>
                    <div class="sk-line" style="width:100%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:78%; height:9px; margin-bottom:10px;"></div>
                    <div class="sk-line" style="width:90%; height:9px;"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- RESULTS -->
    <div class="results" id="results">
        <div class="result-header">
            <h2>Your Video is <span>Ready</span></h2>
        </div>
        <div class="comp-display">
            <div style="color:#555; font-size:12px; margin-bottom:8px; letter-spacing:2px;">SELECTED COMPOSITION</div>
            <div class="comp-name" id="composition"></div>
            <div class="render-cmd" id="renderCmd" onclick="copyCmd()">Click to copy render command</div>
        </div>
        <div class="card">
            <div class="card-header"><div class="card-title">Content Strategy</div></div>
            <pre id="strategy"></pre>
        </div>
        <div class="card">
            <div class="card-header"><div class="card-title">Video Script</div></div>
            <pre id="script"></pre>
        </div>
        <div class="card">
            <div class="card-header">
                <div class="card-title">Remotion Coding Prompt</div>
                <button class="copy-btn" onclick="copyPrompt()">Copy Prompt</button>
            </div>
            <pre id="remotionPrompt"></pre>
        </div>
        <button class="new-btn" onclick="reset()">+ Create Another Video</button>
    </div>
</div>

<script>
    setTimeout(() => {
        document.getElementById('intro').classList.add('hide');
        setTimeout(() => {
            document.getElementById('intro').style.display = 'none';
            document.getElementById('app').classList.add('show');
        }, 800);
    }, 3800);

    document.getElementById('prompt').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generate();
        }
    });

    const thoughts = [
        ['Analyzing your <span>idea</span>...', 'Understanding what makes this unique'],
        ['Selecting the <span>perfect</span> composition...', 'Matching your topic to visual style'],
        ['Building your <span>audience</span> strategy...', 'Who will watch and why they will care'],
        ['Writing <span>cinematic</span> scenes...', 'Every word optimized for animation'],
        ['Generating <span>Remotion</span> code prompt...', 'Pixel-perfect production instructions'],
        ['Scheduling your <span>calendar</span>...', 'Adding this project to your timeline'],
        ['Almost <span>done</span>...', 'Saving everything to your workspace'],
    ];

    let thoughtInterval;

    function startThoughts() {
        let i = 0;
        const el = document.getElementById('loadThought');
        const sub = document.getElementById('loadSub');
        function showNext() {
            el.classList.remove('show');
            setTimeout(() => {
                el.innerHTML = thoughts[i % thoughts.length][0];
                sub.textContent = thoughts[i % thoughts.length][1];
                el.classList.add('show');
                i++;
            }, 400);
        }
        showNext();
        thoughtInterval = setInterval(showNext, 4000);
    }

    async function generate() {
        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt) { alert('Please enter a prompt!'); return; }
        document.getElementById('btn').disabled = true;
        document.getElementById('heroSection').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').style.display = 'none';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        startThoughts();
        const agentIds = ['la1','la2','la3','la4','la5','la6'];
        const barSteps = [8, 25, 45, 65, 82, 95];
        let step = 0;
        const agentInterval = setInterval(() => {
            agentIds.forEach(a => document.getElementById(a).classList.remove('active'));
            if (step < agentIds.length) {
                document.getElementById(agentIds[step]).classList.add('active');
                document.getElementById('wfBarFill').style.width = barSteps[step] + '%';
                step++;
            }
        }, 6000);
        try {
            const res = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await res.json();
            clearInterval(thoughtInterval);
            clearInterval(agentInterval);
            document.getElementById('wfBarFill').style.width = '100%';
            agentIds.forEach(a => document.getElementById(a).classList.add('active'));
            await new Promise(r => setTimeout(r, 600));
            document.getElementById('composition').textContent = data.composition;
            document.getElementById('renderCmd').textContent = data.render_command;
            document.getElementById('renderCmd').setAttribute('data-cmd', data.render_command);
            document.getElementById('strategy').textContent = data.strategy;
            document.getElementById('script').textContent = data.script;
            document.getElementById('remotionPrompt').textContent = data.remotion_coding_prompt;
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch(e) {
            clearInterval(thoughtInterval);
            clearInterval(agentInterval);
            document.getElementById('heroSection').style.display = 'flex';
            document.getElementById('loading').style.display = 'none';
            alert('Error: ' + e.message);
        }
        document.getElementById('btn').disabled = false;
    }

    function reset() {
        document.getElementById('results').style.display = 'none';
        document.getElementById('heroSection').style.display = 'flex';
        document.getElementById('prompt').value = '';
        document.getElementById('wfBarFill').style.width = '0%';
        document.querySelectorAll('.wf-agent-item').forEach(a => a.classList.remove('active'));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function copyCmd() {
        const cmd = document.getElementById('renderCmd').getAttribute('data-cmd');
        navigator.clipboard.writeText(cmd);
        document.getElementById('renderCmd').textContent = 'Copied!';
        setTimeout(() => { document.getElementById('renderCmd').textContent = cmd; }, 2000);
    }

    function copyPrompt() {
        navigator.clipboard.writeText(document.getElementById('remotionPrompt').textContent);
        alert('Remotion prompt copied! Paste it in Cursor or Codex!');
    }

    async function openHistory() {
        document.getElementById('historyPanel').classList.add('show');
        document.getElementById('tasksList').innerHTML = '<div class="h-loading">Loading...</div>';
        document.getElementById('calendarList').innerHTML = '<div class="h-loading">Loading...</div>';
        document.getElementById('notesList').innerHTML = '<div class="h-loading">Loading...</div>';
        try {
            const res = await fetch('/history');
            const data = await res.json();

            // Tasks
            const tEl = document.getElementById('tasksList');
            if (data.tasks && data.tasks.length > 0) {
                tEl.innerHTML = data.tasks.map(t =>
                    '<div class="h-item"><div class="h-item-title">' + (t.title||'Task') + '</div><div class="h-item-sub">Due: ' + (t.due_date||'-') + ' | ' + (t.category||'general') + '</div></div>'
                ).join('');
            } else { tEl.innerHTML = '<div class="h-empty">No tasks yet</div>'; }

            // Calendar
            const cEl = document.getElementById('calendarList');
            if (data.events && data.events.length > 0) {
                cEl.innerHTML = data.events.map(e =>
                    '<div class="h-item"><div class="h-item-title">' + (e.title||'Event') + '</div><div class="h-item-sub">' + (e.date||'-') + ' at ' + (e.time||'-') + '</div></div>'
                ).join('');
            } else { cEl.innerHTML = '<div class="h-empty">No events yet</div>'; }

            // Notes
            const nEl = document.getElementById('notesList');
            if (data.notes && data.notes.length > 0) {
                nEl.innerHTML = data.notes.map(n =>
                    '<div class="h-item"><div class="h-item-title">' + (n.title||'Note') + '</div><div class="h-item-sub">' + (n.tag||'general') + '</div></div>'
                ).join('');
            } else { nEl.innerHTML = '<div class="h-empty">No notes yet</div>'; }

        } catch(e) {
            document.getElementById('tasksList').innerHTML = '<div class="h-empty">Error loading</div>';
            document.getElementById('calendarList').innerHTML = '<div class="h-empty">Error loading</div>';
            document.getElementById('notesList').innerHTML = '<div class="h-empty">Error loading</div>';
        }
    }

    function closeHistory() {
        document.getElementById('historyPanel').classList.remove('show');
    }
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Please provide a prompt!"}), 400
    result = run_agent(prompt)
    return jsonify(result)

@app.route("/history", methods=["GET"])
def history():
    try:
        tasks_data = get_tasks(status="pending")
        events_data = get_calendar_events()
        notes_data = get_notes()
        return jsonify({
            "tasks": tasks_data.get("tasks", []),
            "events": events_data.get("events", []),
            "notes": notes_data.get("notes", [])
        })
    except Exception as e:
        return jsonify({"tasks": [], "events": [], "notes": [], "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
