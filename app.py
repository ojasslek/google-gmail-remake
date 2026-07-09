from flask import Flask, render_template, request, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

app = Flask(__name__)

def make_email(id, sender, email, subject, snippet, date):
    return {'id': id, 'sender': sender, 'email': email, 'subject': subject,
            'snippet': snippet, 'date': date, 'category': None, 'ai_summary': None}

app_state = {
    'is_processed': False,
    'emails': [
        make_email(1,  "Sarah Jenkins",              "sarah.j@acmecorp.com",        "Q3 Project Deadline Extended",           "Hi team, just a quick update that the deadline for the Q3 project has been pushed back by two weeks.",          "10:30 AM"),
        make_email(2,  "Server Alerts",              "noreply@alerts.aws.com",      "CRITICAL: Database Load 98%",            "Automated alert: Primary database cluster read operations have exceeded 98% capacity. Immediate action required.", "09:15 AM"),
        make_email(3,  "Mom",                        "carol99@gmail.com",           "Dinner this weekend?",                   "Hey honey, your dad and I were wondering if you're free for dinner this Sunday?",                               "Yesterday"),
        make_email(4,  "Weekly Tech Digest",         "newsletter@techdigest.io",    "Top 10 Python Libraries",                "Welcome to this week's digest. We explore the newest tools pushing the boundaries of backend development.",       "Yesterday"),
        make_email(5,  "Lottery Winner Notification","winner-claim@weird-domain.xyz","YOU HAVE WON $5,000,000!!!",            "Dear User, your email has been selected as the grand prize winner of the digital lottery.",                       "Oct 24"),
        make_email(6,  "HR Department",              "hr@acmecorp.com",             "Open Enrollment Starts Monday",          "Please review the updated benefits package before open enrollment begins.",                                      "Oct 24"),
        make_email(7,  "Amazon AWS",                 "aws-alerts@amazon.com",       "Action Required: IAM Policy Update",     "Immediate action required to update your IAM policies before they deprecate.",                                   "Oct 23"),
        make_email(8,  "Dad",                        "bob123@gmail.com",            "How is the car?",                        "Just checking in to see if you got the oil changed like I asked.",                                              "Oct 23"),
        make_email(9,  "Python Weekly",              "hello@pythonweekly.com",      "Python Weekly - Issue 600",              "In this newsletter we cover the latest releases in the Python ecosystem.",                                       "Oct 22"),
        make_email(10, "Prince of Nigeria",          "wealthy-prince@scam.com",     "Urgent Business Proposal",               "You are the lucky winner of a $10M trust fund. Please send your bank details immediately.",                       "Oct 22"),
        make_email(11, "Mike from Accounting",       "mike.a@acmecorp.com",         "Expense Report Q2",                      "Can you please send me the updated expense report by EOD?",                                                     "Oct 21"),
        make_email(12, "Security Alert",             "security@acmecorp.com",       "CRITICAL: Vulnerability Detected",       "A critical zero-day vulnerability was found in the main server. Patch immediately.",                             "Oct 21"),
        make_email(13, "Mom",                        "carol99@gmail.com",           "Pictures from the trip",                 "I attached the pictures from our trip to the Grand Canyon. Love, Mom.",                                         "Oct 20"),
        make_email(14, "Morning Brew",               "newsletter@morningbrew.com",  "Market Update",                          "Your daily business newsletter. Markets hit all-time highs today.",                                             "Oct 20"),
        make_email(15, "Prize Claim Center",         "claim@prize-center.xyz",      "Claim your Prize",                       "You are the guaranteed winner of a brand new Tesla! Click here to claim.",                                       "Oct 19"),
        make_email(16, "Elena (Design)",             "elena.d@acmecorp.com",        "New Mockups Ready",                      "I've uploaded the new UI mockups to Figma. Let me know what you think!",                                        "Oct 19"),
        make_email(17, "Dad",                        "bob123@gmail.com",            "BBQ this weekend?",                      "Are you coming over for the BBQ dinner this weekend? Let us know.",                                             "Oct 18"),
        make_email(18, "System Monitor",             "sysmon@acmecorp.com",         "Disk Space Running Low",                 "Immediate action is required. Server disk space is at 99%.",                                                    "Oct 18"),
        make_email(19, "React Digest",               "digest@reactjs.org",          "React 19 Release",                       "Read the digest to learn about all the new features in React 19.",                                              "Oct 17"),
        make_email(20, "Free Vacation",              "vacations@spam.net",          "You won a trip to Hawaii!",              "Enter this exclusive lottery to claim your free vacation package.",                                             "Oct 17"),
        make_email(21, "Project Manager",            "pm@acmecorp.com",             "Sprint Planning Tomorrow",               "We will have our sprint planning meeting tomorrow at 10 AM. Please review the backlog.",                         "Oct 16"),
        make_email(22, "DevOps",                     "devops@acmecorp.com",         "Production Deployment Failed",           "CRITICAL: The production deployment failed. Rollback initiated immediately.",                                    "Oct 16"),
        make_email(23, "Mom",                        "carol99@gmail.com",           "Call me when free",                      "Call me when you get a chance. Your dad and I want to talk.",                                                   "Oct 15"),
        make_email(24, "Data Science Weekly",        "newsletter@datascience.com",  "AI Trends 2026",                         "The best newsletter for data scientists. Discover the newest trends in AI.",                                    "Oct 15"),
        make_email(25, "Lucky Draw",                 "draw@lucky.xyz",              "You are a winner!",                      "Congratulations! You are the winner of our weekly cash lottery draw.",                                          "Oct 14"),
        make_email(26, "Client Feedback",            "feedback@client.com",         "Thoughts on the new design",             "We love the new design, but can we make the logo bigger? Let's discuss.",                                       "Oct 14"),
        make_email(27, "Dad",                        "bob123@gmail.com",            "Mowed the lawn",                         "I finally mowed the lawn. Looks much better now. Come visit soon.",                                             "Oct 13"),
        make_email(28, "AlertManager",               "alerts@acmecorp.com",         "High Latency Detected",                  "Immediate action needed. API response latency is over 5000ms.",                                                 "Oct 13"),
        make_email(29, "Frontend Digest",            "digest@frontend.com",         "CSS Grid Tips & Tricks",                 "Welcome to the CSS grid digest. Master complex layouts in minutes.",                                            "Oct 12"),
        make_email(30, "Million Dollar Lottery",     "lottery@million.com",         "Last chance to claim!",                  "This is your last chance to claim your lottery winnings before they expire.",                                    "Oct 12"),
        make_email(31, "James Wilson",               "j.wilson@acmecorp.com",       "Team Standup Notes",                     "Here are the notes from today's standup. Action items are highlighted in red.",                                 "Oct 11"),
        make_email(32, "PagerDuty",                  "noreply@pagerduty.com",       "CRITICAL: Payment Service Down",         "Incident #4521: Payment processing service is down. Immediate action required.",                                "Oct 11"),
        make_email(33, "Sister",                     "emma_fam@gmail.com",          "Birthday surprise for Mom",              "Hey! I'm planning a surprise dinner for Mom's birthday. Are you in?",                                           "Oct 10"),
        make_email(34, "JavaScript Weekly",          "newsletter@javascriptweekly.com","JavaScript Weekly #700",             "This week: Bun 2.0 is released, Vite 7 benchmarks, and the future of JS bundlers.",                              "Oct 10"),
        make_email(35, "Crypto Guru",                "gains@crypto-moon.xyz",       "DOUBLE your Bitcoin overnight!!!",       "Our secret algorithm guarantees 200% returns. Send 0.5 BTC to get started.",                                     "Oct 9"),
        make_email(36, "Lisa (PM)",                  "lisa.pm@acmecorp.com",        "Roadmap Review Q4",                      "I've shared the Q4 roadmap doc with you. Please add comments before our Friday call.",                          "Oct 9"),
        make_email(37, "Grandma",                    "ruth_g@aol.com",              "Thanksgiving plans?",                    "Hi dear, are you joining us for Thanksgiving dinner? Please let me know soon.",                                  "Oct 8"),
        make_email(38, "Cloud Watch",                "alerts@cloudwatch.aws.com",   "CRITICAL: CPU Spike 100%",               "EC2 instance i-0abc123 CPU has been at 100% for 10 minutes. Immediate action required.",                          "Oct 8"),
        make_email(39, "CSS Tricks",                 "newsletter@css-tricks.com",   "CSS Weekly Roundup",                     "This week's newsletter covers anchor positioning, scroll-driven animations, and more.",                          "Oct 7"),
        make_email(40, "Nigerian Bank",              "transfer@nigerianbank.xyz",   "Funds Transfer Notice",                  "A sum of $8.5M has been designated for you. Reply with your account details.",                                   "Oct 7"),
        make_email(41, "Tom (Engineering)",          "tom.e@acmecorp.com",          "Code Review Request",                    "Hey, can you review my PR? It's blocking the release. Link in the ticket.",                                     "Oct 6"),
        make_email(42, "Datadog",                    "alerts@datadog.com",          "CRITICAL: Error Rate Spike",             "Error rate on /api/checkout has exceeded 50% for the past 5 minutes. Immediate action required.",                 "Oct 6"),
        make_email(43, "Brother",                    "mike_bro@gmail.com",          "Dad's retirement party",                 "We're throwing dad a surprise retirement party next month. Want to help plan?",                                   "Oct 5"),
        make_email(44, "Smashing Magazine",          "newsletter@smashingmagazine.com","Smashing Newsletter #500",            "Frontend insights: Design systems, accessibility audits, and performance budgets.",                               "Oct 5"),
        make_email(45, "Free iPhone",               "claim@free-apple.xyz",        "You've been selected for a FREE iPhone!", "Congratulations! You are our lucky lottery winner. Click now to claim your prize.",                              "Oct 4"),
        make_email(46, "Rachel (HR)",                "rachel.hr@acmecorp.com",      "Performance Review Schedule",            "Your annual performance review is scheduled for Nov 3rd. Please complete the self-assessment form.",              "Oct 4"),
        make_email(47, "Mom",                        "carol99@gmail.com",           "Sent you a care package!",               "Hi sweetheart, I sent you a care package in the mail. It should arrive by Friday!",                              "Oct 3"),
        make_email(48, "Sentry",                     "noreply@sentry.io",           "New Critical Error: NullPointerException","A critical unhandled exception occurred in production. Immediate action required.",                            "Oct 3"),
        make_email(49, "Node Weekly",                "newsletter@nodeweekly.com",   "Node.js Weekly - Issue 550",             "Node 22 LTS is out! Read about the new features, security patches, and more.",                                   "Oct 2"),
        make_email(50, "Fake IRS",                   "irs-refund@tax-claim.xyz",    "Your IRS Tax Refund is Ready",           "Click here to claim your $3,200 tax refund. Provide your SSN to verify identity.",                              "Oct 2"),
        make_email(51, "Kevin (Sales)",              "kevin.s@acmecorp.com",        "Big Deal Closing This Week",             "We're close to closing the Nexus Corp deal. Need final legal approval ASAP.",                                   "Oct 1"),
        make_email(52, "Opsgenie",                   "noreply@opsgenie.com",        "CRITICAL: Memory Leak Detected",         "Production server memory at 99%. Immediate action required to prevent crash.",                                  "Oct 1"),
        make_email(53, "Sister",                     "emma_fam@gmail.com",          "Call me tonight?",                       "Hey! Give me a call when you get home tonight, want to catch up.",                                             "Sep 30"),
        make_email(54, "Dev.to",                     "newsletter@dev.to",           "Top Posts This Week on DEV",             "This week's top reads: How I built a SaaS in 30 days, Rust for web devs, and more.",                             "Sep 30"),
        make_email(55, "Phishing Alert",             "security@paypa1.xyz",         "Verify your PayPal account NOW",         "Unusual activity detected. Lottery of accounts being locked. Verify your details immediately.",                   "Sep 29"),
        make_email(56, "Priya (Design)",             "priya.d@acmecorp.com",        "Updated Brand Guidelines",               "I've updated the brand guidelines doc. Major changes to typography and spacing.",                                "Sep 29"),
        make_email(57, "Dad",                        "bob123@gmail.com",            "Fixed the leaky faucet",                 "Finally fixed that leaky faucet in the kitchen. Feels good to get that done!",                                  "Sep 28"),
        make_email(58, "New Relic",                  "noreply@newrelic.com",        "CRITICAL: Throughput Drop",              "Application throughput dropped by 80% in the last 15 minutes. Immediate action required.",                       "Sep 28"),
        make_email(59, "Bytes Newsletter",           "newsletter@bytes.dev",        "Bytes - Your Weekly JavaScript Digest", "This week: shadcn goes viral again, OpenAI drops a new model, and Deno 3 ships.",                                "Sep 27"),
        make_email(60, "Discount Pills",             "promo@cheap-pharma.xyz",      "Get 90% off on prescription drugs!",     "No prescription needed! Order online now. Lottery of people are saving big.",                                   "Sep 27"),
        make_email(61, "Ops Team",                   "ops@acmecorp.com",            "Scheduled Maintenance Window",           "Reminder: We have a maintenance window this Saturday 2-4 AM. Services will be unavailable.",                     "Sep 26"),
        make_email(62, "Grafana",                    "alerts@grafana.com",          "CRITICAL: Dashboard Alert Fired",        "Alert 'Prod DB Connections' exceeded threshold of 500. Immediate action required.",                              "Sep 26"),
        make_email(63, "Grandma",                    "ruth_g@aol.com",              "Sending prayers your way",               "Just thinking of you dear. Sending lots of love and prayers. Call when you can.",                               "Sep 25"),
        make_email(64, "Hacker Newsletter",          "newsletter@hackernewsletter.com","Hacker Newsletter #700",             "Best of HN this week: a new programming language, a hot startup post-mortem, and more.",                         "Sep 25"),
        make_email(65, "Fake Microsoft",             "support@micros0ft.xyz",       "Your Windows license has expired",       "Your PC is at risk! Click here to renew your Windows license to avoid data loss.",                              "Sep 24"),
        make_email(66, "Alex (Backend)",             "alex.b@acmecorp.com",         "API Rate Limiting Implementation",       "I've drafted the proposal for API rate limiting. Would love your technical review.",                             "Sep 24"),
        make_email(67, "Brother",                    "mike_bro@gmail.com",          "Game night this Friday?",                "Hey, want to come over for game night on Friday? Bringing the whole crew.",                                     "Sep 23"),
        make_email(68, "PagerDuty",                  "noreply@pagerduty.com",       "CRITICAL: Auth Service Timeout",         "Authentication service timing out for 30% of requests. Immediate action required.",                             "Sep 23"),
        make_email(69, "Pointer Newsletter",         "newsletter@pointer.io",       "Pointer #450 - Links for Developers",   "Curated reading for developers: system design, leadership, and code quality.",                                    "Sep 22"),
        make_email(70, "Lottery HQ",                 "hq@lottery-central.xyz",      "Unclaimed Prize: $250,000",              "A lottery prize of $250,000 in your name is unclaimed. Claim before it expires!",                               "Sep 22"),
        make_email(71, "Natalie (QA)",               "natalie.qa@acmecorp.com",     "Regression Test Results",                "All 412 regression tests passed for the v2.4 release candidate. Ready for staging.",                             "Sep 21"),
        make_email(72, "CloudFlare",                 "alerts@cloudflare.com",       "CRITICAL: DDoS Attack Detected",         "Your domain is under a DDoS attack. Immediate action required to enable protection.",                           "Sep 21"),
        make_email(73, "Mom",                        "carol99@gmail.com",           "Saw your favorite movie on TV",          "They were playing that movie you love on TV last night! Made me think of you.",                                 "Sep 20"),
        make_email(74, "TLDR Newsletter",            "newsletter@tldr.tech",        "TLDR - Tech News Summary",               "Today: GitHub Copilot upgrades, Nvidia earnings beat, and a new AI chip startup.",                               "Sep 20"),
        make_email(75, "Scam Alert",                 "refund@amazon-claim.xyz",     "Your Amazon refund of $389 is ready",    "Click to claim your refund. This link expires in 24 hours or your lottery ticket is void.",                    "Sep 19"),
        make_email(76, "Finance Team",               "finance@acmecorp.com",        "Q3 Budget Review Meeting",               "The Q3 budget review is scheduled for Thursday. Please bring your department's actuals.",                       "Sep 19"),
        make_email(77, "Dad",                        "bob123@gmail.com",            "Grandpa's 80th Birthday",                "Don't forget Grandpa's 80th birthday party next weekend! He's really excited.",                                 "Sep 18"),
        make_email(78, "Sentry",                     "noreply@sentry.io",           "CRITICAL: 500 Errors on /checkout",      "50+ users encountering 500 errors on the checkout page. Immediate action required.",                            "Sep 18"),
        make_email(79, "Cooper Press",               "newsletter@cooperpress.com",  "Go Weekly - Issue 480",                  "This week in Go: new generics patterns, profiling tips, and the stdlib additions in 1.23.",                     "Sep 17"),
        make_email(80, "Bank Alert",                 "noreply@yourbank-secure.xyz", "Suspicious Login to Your Account",       "A suspicious lottery login was detected. Click to verify and secure your account now.",                         "Sep 17"),
        make_email(81, "Sam (DevOps)",               "sam.devops@acmecorp.com",     "K8s Cluster Upgrade Plan",               "I've drafted the plan for upgrading our Kubernetes cluster to v1.31. Need your sign-off.",                       "Sep 16"),
        make_email(82, "PagerDuty",                  "noreply@pagerduty.com",       "CRITICAL: Redis Cache Cluster Down",     "Redis cluster is unresponsive. Cache miss rate at 100%. Immediate action required.",                            "Sep 16"),
        make_email(83, "Sister",                     "emma_fam@gmail.com",          "Mom's gift ideas?",                      "Christmas is coming up. Do you have any ideas for what to get Mom and Dad?",                                   "Sep 15"),
        make_email(84, "Sidebar Newsletter",         "newsletter@sidebar.io",       "Sidebar - 5 Design Links",               "5 must-read design articles this week: color theory, microinteractions, and accessibility.",                    "Sep 15"),
        make_email(85, "Fake Google",                "noreply@google-security.xyz", "Google Account Security Alert",          "Your account has been accessed. Lottery selection process. Click here to recover.",                             "Sep 14"),
        make_email(86, "Carlos (Product)",           "carlos.p@acmecorp.com",       "User Research Findings",                 "Sharing the findings from last week's user research sessions. Some really great insights.",                     "Sep 14"),
        make_email(87, "Grandma",                    "ruth_g@aol.com",              "Recipe for your favorite cookies",       "I wrote down the recipe for your favorite chocolate chip cookies. Enjoy!",                                     "Sep 13"),
        make_email(88, "AWS",                        "noreply@aws.amazon.com",      "CRITICAL: S3 Bucket Public Exposed",     "A critical security alert: your S3 bucket is publicly accessible. Immediate action required.",                    "Sep 13"),
        make_email(89, "Syntax FM",                  "newsletter@syntax.fm",        "Syntax Podcast - Episode 810",           "This week Scott and Wes cover CSS container queries, Astro 5, and frontend tooling in 2026.",                  "Sep 12"),
        make_email(90, "Weight Loss Scam",           "burn@fat-pills.xyz",          "Lose 30 lbs in 30 days GUARANTEED",      "Doctor-hated trick melts belly fat overnight. Click here to buy now before the lottery sale ends.",            "Sep 12"),
        make_email(91, "Ian (CEO)",                  "ian.ceo@acmecorp.com",        "All-Hands Meeting Friday",               "Reminder: All-hands meeting this Friday at 2 PM. Big announcements. Please attend.",                            "Sep 11"),
        make_email(92, "Datadog",                    "alerts@datadog.com",          "CRITICAL: Postgres Replication Lag",     "Postgres replica is 30 minutes behind master. Data consistency risk. Immediate action required.",               "Sep 11"),
        make_email(93, "Mom",                        "carol99@gmail.com",           "Your old room is cleaned out",           "Your dad and I finally cleaned out your old room. Found some of your old stuff!",                              "Sep 10"),
        make_email(94, "Changelog Newsletter",       "newsletter@changelog.com",    "Changelog Weekly",                       "Big week in open source: HTMX 2.0 ships, Prettier hits 4.0, and Bun adds FFI.",                                "Sep 10"),
        make_email(95, "Phishing Attempt",           "no-reply@dropbox-secure.xyz", "Your Dropbox storage is full",           "Upgrade now or your files will be permanently deleted. Lottery offer: 50% off.",                              "Sep 9"),
        make_email(96, "Rachel (HR)",                "rachel.hr@acmecorp.com",      "New Hire Onboarding - Week 1",           "Please make sure to block 2 hours on Monday to onboard our two new engineers.",                               "Sep 9"),
        make_email(97, "Brother",                    "mike_bro@gmail.com",          "Check out this video",                   "Bro, you HAVE to watch this, it's hilarious. Sending the link from dad's retirement dinner.",                  "Sep 8"),
        make_email(98, "OpsGenie",                   "noreply@opsgenie.com",        "CRITICAL: SSL Certificate Expiring",     "SSL certificate for api.acmecorp.com expires in 24 hours. Immediate action required.",                         "Sep 8"),
        make_email(99, "The Pragmatic Engineer",     "newsletter@pragmaticengineer.com","The Pragmatic Engineer Newsletter",  "Inside Big Tech engineering: how teams handle incidents, on-call culture, and SLAs.",                          "Sep 7"),
        make_email(100,"Mega Prize Draw",            "win@megaprizdraw.xyz",        "Final notice: $1M Prize Unclaimed",      "This is your absolute last chance to claim your lottery winnings of $1,000,000.",                               "Sep 7"),

        make_email(101,"Jenny (Marketing)",          "jenny.m@acmecorp.com",        "Campaign Launch Next Week",              "The new product launch campaign is locked in for Tuesday. Need final copy approval from your side.",              "Sep 6"),
        make_email(102,"Cloudflare",                 "alerts@cloudflare.com",       "CRITICAL: WAF Rule Triggered",           "Over 10,000 malicious requests blocked in the last hour. Immediate action required to review WAF rules.",          "Sep 6"),
        make_email(103,"Mom",                        "carol99@gmail.com",           "Baked your favorite pie",                "I baked your favorite apple pie today! Come over whenever and I'll save you a slice.",                            "Sep 5"),
        make_email(104,"Go Newsletter",              "newsletter@golangweekly.com",  "Go Weekly - Issue 510",                  "This week: Go 1.23 released, new slices package, and fuzz testing best practices.",                              "Sep 5"),
        make_email(105,"Fake PayPal",                "service@paypa1-secure.xyz",   "Unauthorized transaction detected",      "A $499 transaction was made on your account. Click to dispute and claim your lottery protection.",                 "Sep 4"),
        make_email(106,"Dan (CTO)",                  "dan.cto@acmecorp.com",        "Architecture Decision Record",           "I've drafted the ADR for our move to microservices. Please review and add your comments before Thursday.",        "Sep 4"),
        make_email(107,"Grandma",                    "ruth_g@aol.com",              "Thinking of you",                        "Just wanted to say I love you and I'm proud of you. Call when you can, dear.",                                   "Sep 3"),
        make_email(108,"Prometheus",                 "alerts@prometheus.io",        "CRITICAL: Alert Manager Down",           "Prometheus alert manager is unreachable. Monitoring is blind. Immediate action required.",                        "Sep 3"),
        make_email(109,"Dockerfile Weekly",          "newsletter@dockerfileweekly.com","Docker Weekly - Issue 340",           "Container security, multi-stage builds, and compose v3 tips from the community.",                                "Sep 2"),
        make_email(110,"Crypto Doubler",             "double@trustmebro.xyz",       "Double your ETH in 24 hours",            "Our AI-powered algorithm guarantees returns. This exclusive lottery of investors is closing soon.",               "Sep 2"),
        make_email(111,"Sophia (Legal)",             "sophia.legal@acmecorp.com",   "NDA for New Vendor",                     "Please review and sign the NDA for the Apex Dynamics vendor agreement by Friday.",                              "Sep 1"),
        make_email(112,"AWS CloudWatch",             "alerts@cloudwatch.aws.com",   "CRITICAL: Lambda Timeout Spike",         "Lambda function process-payments timing out at 30% rate. Immediate action required.",                            "Sep 1"),
        make_email(113,"Brother",                    "mike_bro@gmail.com",          "Fantasy football draft tonight",         "Don't forget! Fantasy football draft is at 8 PM tonight. Be there or miss your picks.",                          "Aug 31"),
        make_email(114,"Ruby Weekly",                "newsletter@rubyweekly.com",   "Ruby Weekly - Issue 670",                "Ruby 3.4 features, Hotwire tips, and the Rails 8 upgrade guide.",                                               "Aug 31"),
        make_email(115,"Survey Scam",                "rewards@survey-cash.xyz",     "Complete survey - earn $500 TODAY",      "You've been selected to earn $500! Complete a 2-minute lottery survey now.",                                     "Aug 30"),
        make_email(116,"Marco (Backend)",            "marco.b@acmecorp.com",        "Database Migration Complete",            "The Postgres 15 migration finished successfully. Zero downtime. All data verified.",                             "Aug 30"),
        make_email(117,"Dad",                        "bob123@gmail.com",            "Happy Tuesday!",                         "Hope your week is going well, son. Just thinking of you. Come visit when you can!",                              "Aug 29"),
        make_email(118,"Sentry",                     "noreply@sentry.io",           "CRITICAL: Memory Quota Exceeded",        "Worker pod memory exceeded 4GB limit and was OOMKilled. Immediate action required.",                            "Aug 29"),
        make_email(119,"TLDR Web Dev",               "newsletter@tldr.tech",        "TLDR Web Dev",                           "SolidJS hits v2, Remix gets a new router, and Next.js 15 RC drops today.",                                     "Aug 28"),
        make_email(120,"Gift Card Scam",             "gifts@free-giftcards.xyz",    "$1000 Amazon Gift Card WAITING",         "You've been chosen for a free $1000 Amazon gift card. Claim your lottery reward before midnight.",                 "Aug 28"),
        make_email(121,"Tina (QA)",                  "tina.qa@acmecorp.com",        "Flaky Tests Report",                     "12 tests are intermittently failing in CI. I've filed tickets for each. Needs engineering triage.",               "Aug 27"),
        make_email(122,"PagerDuty",                  "noreply@pagerduty.com",       "CRITICAL: Checkout Flow 503 Errors",     "Users unable to complete checkout. Error rate 80%. Immediate action required.",                                  "Aug 27"),
        make_email(123,"Sister",                     "emma_fam@gmail.com",          "New apartment photos!",                  "I finally moved in! Sending over some photos of the new place. Come visit soon!",                               "Aug 26"),
        make_email(124,"Frontend Masters",           "newsletter@frontendmasters.com","Frontend Masters Newsletter",          "New courses: Advanced CSS, TypeScript deep dive, and React Server Components.",                                "Aug 26"),
        make_email(125,"Fake Apple",                 "support@app1e-billing.xyz",   "Your iCloud storage is full",            "Upgrade now or your lottery-protected backup will be deleted in 24 hours.",                                    "Aug 25"),
        make_email(126,"Victor (Infra)",             "victor.i@acmecorp.com",       "Terraform Plan for Prod",                "Sharing the Terraform plan for the infrastructure changes. Please approve before 5 PM.",                        "Aug 25"),
        make_email(127,"Mom",                        "carol99@gmail.com",           "Your old friend called",                 "Your old friend Jamie called looking for you. I gave them your number. Hope that's okay!",                      "Aug 24"),
        make_email(128,"Grafana",                    "alerts@grafana.com",          "CRITICAL: Disk I/O Saturation",          "Production server disk I/O at 100% for 15 minutes. Immediate action required.",                                 "Aug 24"),
        make_email(129,"Kotlin Weekly",              "newsletter@kotlinweekly.com",  "Kotlin Weekly - Issue 380",              "Kotlin 2.1 ships! Multiplatform updates, coroutines deep dive, and KSP tips.",                                  "Aug 23"),
        make_email(130,"Weight Loss Pill",           "slim@keto-magic.xyz",         "Melt fat while you sleep!",              "Doctors don't want you to know this trick. Claim your lottery discount before stock runs out.",                  "Aug 23"),
        make_email(131,"Amy (People Ops)",           "amy.po@acmecorp.com",         "Team Offsite Planning",                  "We're planning the Q4 team offsite. Please fill out the availability poll by end of week.",                     "Aug 22"),
        make_email(132,"New Relic",                  "noreply@newrelic.com",        "CRITICAL: Apdex Score Critical",         "Application performance index dropped to 0.45. Users experiencing slowness. Immediate action required.",        "Aug 22"),
        make_email(133,"Dad",                        "bob123@gmail.com",            "Watched your old baseball game",         "Found the tape of your championship game from high school. Brought back so many memories!",                    "Aug 21"),
        make_email(134,"Software Lead Weekly",       "newsletter@softwareleadweekly.com","Software Lead Weekly",              "Engineering leadership: team topologies, 1:1 templates, and managing technical debt.",                         "Aug 21"),
        make_email(135,"Phishing",                   "verify@your-account-alert.xyz","Verify your account NOW",               "Suspicious activity detected. Your lottery account will be locked in 12 hours. Verify now.",                   "Aug 20"),
        make_email(136,"Neil (Data)",                "neil.data@acmecorp.com",      "Snowflake Cost Report",                  "Our Snowflake spend is up 35% this quarter. Sharing the breakdown — worth a conversation.",                    "Aug 20"),
        make_email(137,"Grandma",                    "ruth_g@aol.com",              "Made your favorite soup",                "Made a big pot of chicken noodle soup. I'll have a container ready for you when you visit!",                   "Aug 19"),
        make_email(138,"Datadog",                    "alerts@datadog.com",          "CRITICAL: Network Packet Loss",          "15% packet loss detected on prod-db-01 network interface. Immediate action required.",                         "Aug 19"),
        make_email(139,"iOS Dev Weekly",             "newsletter@iosdevweekly.com",  "iOS Dev Weekly - Issue 620",             "Swift 6 migration tips, visionOS updates, and the new Xcode 16 features.",                                    "Aug 18"),
        make_email(140,"Free Robux Scam",            "robux@free-gaming.xyz",       "1,000,000 FREE Robux Waiting!",          "Claim your free Robux now! This lottery ends tonight. No surveys needed — just click!",                         "Aug 18"),
        make_email(141,"Rachel (HR)",                "rachel.hr@acmecorp.com",      "Policy Update: Remote Work",             "Updated remote work policy effective Oct 1st. Please read and acknowledge by end of this week.",                "Aug 17"),
        make_email(142,"OpsGenie",                   "noreply@opsgenie.com",        "CRITICAL: Health Check Failed",          "Load balancer health checks failing for 3 backend nodes. Immediate action required.",                          "Aug 17"),
        make_email(143,"Sister",                     "emma_fam@gmail.com",          "Lunch this week?",                       "Hey! Are you free for lunch sometime this week? Would love to catch up in person.",                            "Aug 16"),
        make_email(144,"Hacker News Digest",         "newsletter@hndigest.com",     "HN Digest - Top Stories",                "Top 10 Hacker News stories this week: AI, compilers, and a viral programming post.",                           "Aug 16"),
        make_email(145,"Fake Netflix",               "billing@netf1ix-renew.xyz",   "Your Netflix subscription expired",      "Renew now to keep watching. Your lottery offer of 3 months free expires tonight.",                            "Aug 15"),
        make_email(146,"Leo (Frontend)",             "leo.fe@acmecorp.com",         "Accessibility Audit Results",            "Completed the WCAG 2.2 audit. We have 14 issues to fix before launch. Sharing the report.",                   "Aug 15"),
        make_email(147,"Brother",                    "mike_bro@gmail.com",          "Concert tickets?",                       "There's a concert next Saturday. You in? Tickets are going fast so let me know today.",                        "Aug 14"),
        make_email(148,"AWS",                        "noreply@aws.amazon.com",      "CRITICAL: RDS Failover Initiated",       "Primary RDS instance unresponsive. Automated failover to replica in progress. Immediate action required.",     "Aug 14"),
        make_email(149,"StatusCode Weekly",          "newsletter@statuscode.io",    "StatusCode Weekly - Issue 310",          "HTTP, REST, and APIs: best practices, new specs, and the GraphQL vs REST debate continues.",                    "Aug 13"),
        make_email(150,"Miracle Cure Scam",          "cure@miracle-health.xyz",     "Doctors HATE this one trick",            "Cure diabetes, arthritis & more with this lottery-approved supplement. Order today!",                         "Aug 13"),
        make_email(151,"Ian (CEO)",                  "ian.ceo@acmecorp.com",        "Strategic Review Deck",                  "Sharing the strategic review deck for the board meeting. Please send feedback before Sunday.",                "Aug 12"),
        make_email(152,"Cloudflare",                 "alerts@cloudflare.com",       "CRITICAL: Origin Server Unreachable",    "Cloudflare unable to reach origin server for acmecorp.com. Immediate action required.",                      "Aug 12"),
        make_email(153,"Mom",                        "carol99@gmail.com",           "Proud of you!",                          "Saw your name in the company newsletter. Your dad and I are so proud of everything you do!",                  "Aug 11"),
        make_email(154,"Architecture Weekly",        "newsletter@architectureweekly.com","Architecture Weekly #200",          "Event sourcing in practice, saga patterns, and team-first microservices decomposition.",                      "Aug 11"),
        make_email(155,"Prince's Assistant",         "secretary@royalwealth.xyz",   "Confidential: Royal Fund Transfer",      "I am writing on behalf of a royal family. You are selected to receive $22M. Respond immediately.",            "Aug 10"),
    ]
}

TRAINING_DATA = [
    # Urgent
    ("Server load at 98%. Action required.", "urgent"),
    ("CRITICAL: Database load exceeded 98% capacity.", "urgent"),
    ("Incident #4521: Payment processing service is down.", "urgent"),
    ("CPU Spike 100%. Alert manager down.", "urgent"),
    ("Error rate on checkout page has exceeded 50%.", "urgent"),
    ("OOMKilled: Worker pod memory exceeded limit.", "urgent"),
    ("Production deployment failed. Rollback initiated.", "urgent"),
    ("CRITICAL: Disk Space Running Low at 99%.", "urgent"),
    ("Vulnerability Detected in main server. Patch immediately.", "urgent"),
    ("DDoS Attack Detected on primary domain.", "urgent"),
    ("High Latency Alert: response time > 5000ms.", "urgent"),
    ("SSL Certificate Expiring in 24 hours. Action required.", "urgent"),
    ("RDS Failover Initiated. Primary database down.", "urgent"),
    ("Network Packet Loss: 15% packet loss on DB.", "urgent"),

    # Work
    ("Sprint Planning Agenda. Please review the backlog.", "work"),
    ("Q3 Project Deadline Extended by two weeks.", "work"),
    ("Q3 Budget Review Meeting scheduled.", "work"),
    ("Figma mockups are ready. Please review.", "work"),
    ("Expense Report for Q2 needs approval.", "work"),
    ("Weekly Team Standup Notes and action items.", "work"),
    ("Review the roadmap for Q4 and add comments.", "work"),
    ("NDA for Apex Dynamics vendor agreement.", "work"),
    ("Terraform plans for production infrastructure.", "work"),
    ("Cost report for Snowflake usage analysis.", "work"),
    ("Updated brand guidelines and typography.", "work"),
    ("Accessibility audit report for web app.", "work"),
    ("Code review request for authentication branch.", "work"),
    ("Updated remote work policy document.", "work"),

    # Personal
    ("Are you free for dinner this Sunday? Let us know.", "personal"),
    ("Dad wants to know if you got the oil changed.", "personal"),
    ("Pictures from the family trip to the Grand Canyon.", "personal"),
    ("Wanna hang out this weekend for BBQ?", "personal"),
    ("Mom sent a care package to your apartment.", "personal"),
    ("Birthday surprise party planning for Mom.", "personal"),
    ("Recipe for Grandpa's favorite cookies.", "personal"),
    ("Planning dad's retirement surprise dinner.", "personal"),
    ("Want to meet up for lunch this week?", "personal"),
    ("Game night this Friday at my place.", "personal"),
    ("Do you want concert tickets for next Saturday?", "personal"),
    ("Grandma sending thoughts and prayers.", "personal"),
    ("Your old room is finally cleaned out.", "personal"),
    ("Emma got a new apartment and sent photos.", "personal"),

    # News
    ("Python Weekly Digest - Issue 600.", "news"),
    ("Top 10 Python Libraries for machine learning.", "news"),
    ("Morning Brew Business Newsletter.", "news"),
    ("React 19 Release Notes and updates.", "news"),
    ("Kotlin Weekly Newsletter - Issue 380.", "news"),
    ("Weekly Tech Digest for backend developers.", "news"),
    ("Javascript Weekly Issue 700: Bun and Vite.", "news"),
    ("TLDR Newsletter: Tech and AI summaries.", "news"),
    ("Go Weekly issue 480: generics and profiling.", "news"),
    ("Hacker News digest: top developer posts.", "news"),
    ("Changelog Weekly: open source tech updates.", "news"),
    ("Pragmatic Engineer: on-call engineering culture.", "news"),

    # Spam
    ("YOU HAVE WON A LOTTERY PRIZE OF $5,000,000!!!", "spam"),
    ("Earn money fast online. Claim your reward.", "spam"),
    ("Double your Bitcoin in 24 hours guaranteed.", "spam"),
    ("Claim your free iPhone lottery prize now.", "spam"),
    ("Melt fat overnight with keto weight loss pills.", "spam"),
    ("Your Windows license has expired. Renew to avoid risk.", "spam"),
    ("Claim your $250,000 unclaimed lottery funds.", "spam"),
    ("Get 90% off prescription drug prices today.", "spam"),
    ("Verify your PayPal account login immediately.", "spam"),
    ("iCloud storage is full. Verify billing details.", "spam"),
    ("Urgent business proposal from Nigeria prince.", "spam"),
    ("Lottery notification: win cash prize.", "spam"),
    ("Netflix subscription billing problem. Update account.", "spam"),
    ("Robux generator: 1,000,000 free Robux today.", "spam"),
]

def extract_key_words(text, n=6):
    """Return the first n meaningful words, skipping filler openers."""
    fillers = {'hi', 'hey', 'hello', 'dear', 'just', 'a', 'the', 'an',
               'your', 'we', 'i', 'our', 'this', 'that', 'is', 'are',
               'have', 'has', 'been', 'to', 'in', 'for', 'of', 'and', 'you'}
    words = [w.strip('.,!?') for w in text.split() if w.lower().strip('.,!?') not in fillers]
    return ' '.join(words[:n])


def generate_summary(email, category):
    """Generate a unique, clean ~10-word summary sentence per email."""
    sender  = email['sender'].split('(')[0].strip()   # "Elena (Design)" → "Elena"
    subject = (email['subject']
               .replace('CRITICAL:', '').replace('Action Required:', '')
               .replace('!!!', '').strip())
    snippet = email['snippet'].strip()

    if category == 'urgent':
        key = extract_key_words(snippet, 5)
        return f"Urgent: {subject}. {key}."

    elif category == 'spam':
        return f"Suspicious email from unknown sender. Do not click any links."

    elif category == 'personal':
        key = extract_key_words(snippet, 7)
        return f"{sender} says: {key}."

    elif category == 'news':
        key = extract_key_words(snippet, 7)
        return f"{sender}: {key}."

    else:  # work
        key = extract_key_words(snippet, 7)
        return f"{sender} — {key}."


def process_emails_with_ai():
    # Prepare training lists
    X_train = [text for text, label in TRAINING_DATA]
    y_train = [label for text, label in TRAINING_DATA]

    # Build Pipeline (TF-IDF vectorizer + Naive Bayes Classifier)
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('nb', MultinomialNB(alpha=0.1))
    ])

    # Fit pipeline model
    model.fit(X_train, y_train)

    # Predict categories for inbox emails
    for email in app_state['emails']:
        text_to_classify = f"{email['subject']} {email['snippet']}"
        predicted_category = model.predict([text_to_classify])[0]

        email['category'] = predicted_category
        email['ai_summary'] = generate_summary(email, predicted_category)

process_emails_with_ai()
app_state['is_processed'] = True

@app.route('/')
def index():
    category_filter = request.args.get('category', 'all')
    filtered_emails = app_state['emails']
    if category_filter != 'all':
        filtered_emails = [e for e in app_state['emails'] if e.get('category') == category_filter]
    return render_template(
        'index.html',
        emails=filtered_emails,
        all_emails=app_state['emails'],
        active_category=category_filter
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
