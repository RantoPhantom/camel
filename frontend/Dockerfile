FROM node:18-alpine AS base

WORKDIR /frontend

RUN apk add --no-cache curl

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "npm", "start" ]
