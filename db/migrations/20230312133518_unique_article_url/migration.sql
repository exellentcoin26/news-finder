/*
  Warnings:

  - A unique constraint covering the columns `[url]` on the table `NewsArticles` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "NewsArticles_url_key" ON "NewsArticles"("url");
