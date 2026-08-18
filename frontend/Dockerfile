FROM node:20-alpine

WORKDIR /app

ARG VITE_LINK
ENV VITE_LINK=$VITE_LINK

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]