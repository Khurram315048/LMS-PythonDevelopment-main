
document.addEventListener('DOMContentLoaded', function() {
    
    const profileLinks = document.querySelectorAll('.view-profile');
    const modalElement = document.getElementById('studentProfileModal');
    
    
    const profileModal = new bootstrap.Modal(modalElement);

    profileLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault(); 

            
            const name = this.getAttribute('data-name');
            const reg = this.getAttribute('data-reg');
            const phone = this.getAttribute('data-contact');
            const email = this.getAttribute('data-email');
            const program = this.getAttribute('data-program');
            const semester = this.getAttribute('data-semester');
            const pic = this.getAttribute('data-pic');

            
            document.getElementById('modal-student-name').innerText = name;
            document.getElementById('modal-reg').innerText = reg;
            document.getElementById('modal-contact').innerText = phone;
            document.getElementById('modal-email').innerText = email;
            document.getElementById('modal-program').innerText = program;
            document.getElementById('modal-semester').innerText = semester;

            
            const picContainer = document.getElementById('profile-pic-container');
            if (pic && pic.trim() !== "" && !pic.includes('None')) {
                picContainer.innerHTML = `<img src="${pic}" class="rounded-circle shadow" width="120" height="120" style="object-fit: cover; border: 4px solid #fff;">`;
            } else {
                picContainer.innerHTML = `<div class="bg-secondary rounded-circle mx-auto d-flex align-items-center justify-content-center shadow" style="width: 120px; height: 120px; border: 4px solid #fff;">
                                            <i class="fa-solid fa-user fa-4x text-white"></i>
                                          </div>`;
            }

          
            profileModal.show();
        });
    });
});