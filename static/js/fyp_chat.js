



document.addEventListener("DOMContentLoaded",function(){
    const wsInfo=document.getElementById("ws-info");
    if(!wsInfo) return; 

    const fypId=wsInfo.getAttribute("data-fyp-id");
    const userType=wsInfo.getAttribute("data-user-type");
    const userId=wsInfo.getAttribute("data-user-id");

    const protocol=window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl=`${protocol}://${window.location.host}/ws/fyp_chat/${fypId}/${userType}/${userId}`;
    
    const socket=new WebSocket(wsUrl);
    
    const chatBox=document.getElementById("chat-box"); 
    const chatForm=document.getElementById("chat-form");
    const messageInput=document.getElementById("message-input");

    socket.onmessage=function(event){
        const data=JSON.parse(event.data);
        
        const noHistoryMsg=document.getElementById("no-history-msg");
        if(noHistoryMsg){
            noHistoryMsg.remove();
        }

        const messageElement=document.createElement("div");
        const isMe=(data.sender_id == userId && data.sender_type == userType);

        messageElement.className=`d-flex mb-3 ${isMe ? 'justify-content-end' : 'justify-content-start'}`;
        const senderRole=isMe ? 'YOU':(data.sender_type === 'teacher' ?'SUPERVISOR':'STUDENT');
        const now=new Date();
        const timeString=now.getFullYear() + "-" + 
                           String(now.getMonth() + 1).padStart(2, '0') + "-" + 
                           String(now.getDate()).padStart(2, '0') + " " + 
                           String(now.getHours()).padStart(2, '0') + ":" + 
                           String(now.getMinutes()).padStart(2, '0') + ":" + 
                           String(now.getSeconds()).padStart(2, '0');

        
        messageElement.innerHTML=`
            <div class="p-3 shadow-sm rounded-3" style="max-width:80%; background:white; color:#333; border:1px solid #ddd;">
                <small class="d-block fw-bold mb-1" style="font-size:0.7rem; opacity:0.8;">
                    ${senderRole}
                </small>
                <p class="mb-1">${data.message}</p>
                <small class="d-block text-end" style="font-size:0.65rem; opacity:0.7;">${timeString}</small>
            </div>
        `;
        
        chatBox.appendChild(messageElement);
        messageElement.scrollIntoView({behavior:"smooth"});
    };

    chatForm.addEventListener("submit",function(event){
        event.preventDefault(); 
        
        const message=messageInput.value.trim();
        if(message){
            socket.send(message); 
            messageInput.value=""; 
        }
    });
});