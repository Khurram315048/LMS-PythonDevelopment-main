



document.addEventListener("DOMContentLoaded",function(){
    
    const wsInfos=document.querySelectorAll('.teacher-ws-info');
    wsInfos.forEach(info =>{
        const fypId=info.getAttribute("data-fyp-id");
        const userType=info.getAttribute("data-user-type");
        const userId=info.getAttribute("data-user-id");
        const protocol=window.location.protocol==="https:"?"wss":"ws";
        const wsUrl=`${protocol}://${window.location.host}/ws/fyp_chat/${fypId}/${userType}/${userId}`;
        const socket=new WebSocket(wsUrl);

        const chatBox=document.getElementById(`teacher-chat-box-${fypId}`);
        const messageInput=document.getElementById(`teacher-message-input-${fypId}`);
        
        socket.onmessage=function(event){
            const data=JSON.parse(event.data);
            const noHistoryMsg=document.getElementById(`no-history-${fypId}`);
            if(noHistoryMsg){
                noHistoryMsg.remove();
            }

            const messageElement=document.createElement("div");
            const isMe=(data.sender_id==userId && data.sender_type==userType);

            messageElement.className=`d-flex mb-2 ${isMe? 'justify-content-end':'justify-content-start'}`;
            
            const now=new Date();
            let hours=now.getHours();
            let minutes=now.getMinutes();
            const ampm=hours >= 12 ?'PM':'AM';
            hours=hours % 12;
            hours=hours ? hours : 12; 
            minutes=minutes<10?'0'+minutes:minutes;
            const timeString=hours + ':' + minutes + ' ' + ampm;

            messageElement.innerHTML=`
                <div class="chat-bubble ${isMe ? 'msg-teacher' : 'msg-student'}">
                <p class="mb-0" style="font-size: 0.95rem;"></p>
                    <small class="text-muted d-block text-end" style="font-size: 0.7rem;">
                        ${timeString}
                    </small>
                </div>
            `;

            messageElement.querySelector("p").textContent=data.message;
            chatBox.appendChild(messageElement);
            chatBox.scrollTop=chatBox.scrollHeight;
        };

        const chatForm=document.querySelector(`.teacher-chat-form[data-fyp-id="${fypId}"]`);
        if(chatForm){
            chatForm.addEventListener("submit",function(event){
                event.preventDefault(); 
                
                const message=messageInput.value.trim();
                if(message && socket.readyState===WebSocket.OPEN){
                    socket.send(message); 
                    messageInput.value=""; 
                }
            });
        }
    });
});