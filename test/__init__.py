response = """"<html lang="en-gb"><head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8">

		<title>vulnerability: reflected cross site scripting (xss) :: damn vulnerable web application (dvwa)</title>

		<link rel="stylesheet" type="text/css" href="../../dvwa/css/main.css">

		<link rel="icon" type="\image/ico" href="../../favicon.ico">

		<script type="text/javascript" src="../../dvwa/js/dvwapage.js"></script>

	</head>

	<body class="home">
		<div id="container">

			<div id="header">

				<img src="../../dvwa/images/logo.png" alt="damn vulnerable web application">

			</div>

			<div id="main_menu">

				<div id="main_menu_padded">
				<ul class="menublocks"><li class=""><a href="../../.">home</a></li>
<li class=""><a href="../../instructions.php">instructions</a></li>
<li class=""><a href="../../setup.php">setup / reset db</a></li>
</ul><ul class="menublocks"><li class=""><a href="../../vulnerabilities/brute/">brute force</a></li>
<li class=""><a href="../../vulnerabilities/exec/">command injection</a></li>
<li class=""><a href="../../vulnerabilities/csrf/">csrf</a></li>
<li class=""><a href="../../vulnerabilities/fi/.?page=include.php">file inclusion</a></li>
<li class=""><a href="../../vulnerabilities/upload/">file upload</a></li>
<li class=""><a href="../../vulnerabilities/captcha/">insecure captcha</a></li>
<li class=""><a href="../../vulnerabilities/sqli/">sql injection</a></li>
<li class=""><a href="../../vulnerabilities/sqli_blind/">sql injection (blind)</a></li>
<li class=""><a href="../../vulnerabilities/weak_id/">weak session ids</a></li>
<li class=""><a href="../../vulnerabilities/xss_d/">xss (dom)</a></li>
<li class="selected"><a href="../../vulnerabilities/xss_r/">xss (reflected)</a></li>
<li class=""><a href="../../vulnerabilities/xss_s/">xss (stored)</a></li>
<li class=""><a href="../../vulnerabilities/csp/">csp bypass</a></li>
<li class=""><a href="../../vulnerabilities/javascript/">javascript</a></li>
<li class=""><a href="../../vulnerabilities/authbypass/">authorisation bypass</a></li>
<li class=""><a href="../../vulnerabilities/open_redirect/">open http redirect</a></li>
</ul><ul class="menublocks"><li class=""><a href="../../security.php">dvwa security</a></li>
<li class=""><a href="../../phpinfo.php">php info</a></li>
<li class=""><a href="../../about.php">about</a></li>
</ul><ul class="menublocks"><li class=""><a href="../../logout.php">logout</a></li>
</ul>
				</div>

			</div>

			<div id="main_body">

				
<div class="body_padded">
	<h1>vulnerability: reflected cross site scripting (xss)</h1>

	<div class="vulnerable_code_area">
		<form name="xss" action="#" method="get">
			<p>
				what's your name?
				<input type="text" name="name">
				<input type="submit" value="submit">
			</p>

		</form>
		<pre>hello v3dm0s</pre>
	</div>

	<h2>more information</h2>
	<ul>
		<li><a href="https://owasp.org/www-community/attacks/xss/" target="_blank">https://owasp.org/www-community/attacks/xss/</a></li>
		<li><a href="https://owasp.org/www-community/xss-filter-evasion-cheatsheet" target="_blank">https://owasp.org/www-community/xss-filter-evasion-cheatsheet</a></li>
		<li><a href="https://en.wikipedia.org/wiki/cross-site_scripting" target="_blank">https://en.wikipedia.org/wiki/cross-site_scripting</a></li>
		<li><a href="http://www.cgisecurity.com/xss-faq.html" target="_blank">http://www.cgisecurity.com/xss-faq.html</a></li>
		<li><a href="http://www.scriptalert1.com/" target="_blank">http://www.scriptalert1.com/</a></li>
	</ul>
</div>

				<br><br>
				

			</div>

			<div class="clear">
			</div>

			<div id="system_info">
				<input type="button" value="view help" class="popup_button" id="help_button" data-help-url="../../vulnerabilities/view_help.php?id=xss_r&amp;security=low&amp;locale=en" )"=""> <input type="button" value="view source" class="popup_button" id="source_button" data-source-url="../../vulnerabilities/view_source.php?id=xss_r&amp;security=low" )"=""> <div align="left"><em>username:</em> admin<br><em>security level:</em> low<br><em>locale:</em> en<br><em>sqli db:</em> mysql</div>
			</div>

			<div id="footer">

				<p>damn vulnerable web application (dvwa)</p>
				<script src="../../dvwa/js/add_event_listeners.js"></script>

			</div>

		</div>

	

</body></html>"""
occ = dict()
occ[2794] = {
    "context": 'html',
    'detail': {},
    'position': 2794,
    'score': {
        '<': 60,
        '>': 60
    }
}
xsschecker = 'v3dm0s'

test2Str=""" <html>
    <test src="v3dm0s"></test>>
    <ac a="v3dm0s"></ac>>
    <r 2="v3dm0s"></r>>
    </html>>"""