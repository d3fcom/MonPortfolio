// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        gsap.to(window, {duration: 1, scrollTo: target, ease: 'power2.inOut'});
    });
});

// Animations
gsap.registerPlugin(ScrollTrigger);

document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const isDarkMode = localStorage.getItem('darkMode') === 'true';

    // Set initial dark mode state
    if (isDarkMode) {
        body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    darkModeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        darkModeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // Typing effect for main title
    const mainTitle = document.querySelector('h1');
    if (mainTitle) {
        const text = mainTitle.textContent;
        mainTitle.textContent = '';
        const tl = gsap.timeline();
        tl.to(mainTitle, {duration: 0.1, opacity: 1})
          .from(mainTitle, {
            duration: 2,
            onUpdate: function() {
                mainTitle.textContent = text.substr(0, Math.floor(this.progress() * text.length));
            }
          });
    }

    // Hero content animation
    gsap.from('.hero-content', {
        duration: 1,
        y: 50,
        opacity: 0,
        ease: 'power3.out',
        delay: 0.5
    });

    // Staggered fade-in effect for skills section
    gsap.from('#skills .skill-item', {
        scrollTrigger: {
            trigger: '#skills',
            start: 'top center'
        },
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.2,
        ease: 'power3.out'
    });

    // Hover animations for project cards
    const projectCards = document.querySelectorAll('#github-projects .project-item');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {duration: 0.3, scale: 1.05, boxShadow: '0 10px 20px rgba(0,0,0,0.2)'});
        });
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {duration: 0.3, scale: 1, boxShadow: '0 0 0 rgba(0,0,0,0)'});
        });
    });

    // Hover animations for NFT collection images
    const nftImages = document.querySelectorAll('#nft .nft-preview');
    nftImages.forEach(image => {
        image.addEventListener('mouseenter', () => {
            gsap.to(image, {duration: 0.3, scale: 1.1, boxShadow: '0 10px 20px rgba(0,0,0,0.2)'});
        });
        image.addEventListener('mouseleave', () => {
            gsap.to(image, {duration: 0.3, scale: 1, boxShadow: '0 0 0 rgba(0,0,0,0)'});
        });
    });

    // Parallax scrolling effect for background
    gsap.to('.tech-bg', {
        backgroundPosition: `50% ${innerHeight / 2}px`,
        ease: "none",
        scrollTrigger: {
            trigger: "body",
            start: "top top",
            end: "bottom bottom",
            scrub: 1
        }
    });

    // Projects animation
    const projectsContainer = document.getElementById('github-projects');
    if (projectsContainer) {
        gsap.from('#github-projects .project-item', {
            scrollTrigger: {
                trigger: '#projects',
                start: 'top center'
            },
            duration: 0.8,
            y: 50,
            opacity: 0,
            stagger: 0.2,
            ease: 'power3.out'
        });
    }
});

// GitHub Stats
fetch('/github_stats')
    .then(response => response.json())
    .then(data => {
        console.log('GitHub Stats:', data);
        if (data.error) {
            console.error('Error fetching GitHub stats:', data.error);
            return;
        }
        document.getElementById('repo-count').textContent = data.public_repos;
        document.getElementById('followers-count').textContent = data.followers;
        document.getElementById('following-count').textContent = data.following;
    })
    .catch(error => console.error('Error fetching GitHub stats:', error));

// GitHub Projects
fetch('/github_projects')
    .then(response => response.json())
    .then(projects => {
        console.log('GitHub Projects:', projects);
        if (projects.error) {
            console.error('Error fetching GitHub projects:', projects.error);
            return;
        }
        const projectsContainer = document.getElementById('github-projects');
        projectsContainer.innerHTML = ''; // Clear existing content
        projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'project-item bg-gray-800 p-6 rounded-lg';
            projectElement.innerHTML = `
                <h3 class="text-xl font-semibold mb-2">${project.name}</h3>
                <p class="mb-4">${project.description || 'No description available.'}</p>
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-400">${project.language || 'N/A'}</span>
                    <a href="/project/${project.name}" class="text-blue-400 hover:text-blue-300">View Details</a>
                </div>
            `;
            projectsContainer.appendChild(projectElement);
        });
    })
    .catch(error => console.error('Error fetching GitHub projects:', error));

// GitHub Activity Calendar
fetch('/github_activity')
    .then(response => response.json())
    .then(data => {
        console.log('GitHub Activity:', data);
        if (data.error) {
            console.error('Error fetching GitHub activity:', data.error);
            return;
        }
        const calendarContainer = document.getElementById('github-calendar');
        const calendar = createCalendar(data);
        calendarContainer.innerHTML = calendar;
    })
    .catch(error => console.error('Error fetching GitHub activity:', error));

function createCalendar(data) {
    const today = new Date();
    const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
    let calendar = '<div class="github-calendar-grid">';

    for (let d = new Date(oneYearAgo); d <= today; d.setDate(d.getDate() + 1)) {
        const dateString = d.toISOString().split('T')[0];
        const count = data[dateString] || 0;
        const intensity = getIntensityClass(count);
        calendar += `<div class="day ${intensity}" title="${dateString}: ${count} contributions"></div>`;
    }

    calendar += '</div>';
    return calendar;
}

function getIntensityClass(count) {
    if (count === 0) return 'intensity-0';
    if (count < 5) return 'intensity-1';
    if (count < 10) return 'intensity-2';
    if (count < 15) return 'intensity-3';
    return 'intensity-4';
}