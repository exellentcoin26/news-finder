/*
  Warnings:

  - A unique constraint covering the columns `[id,url]` on the table `NewsArticles` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateTable
CREATE TABLE "UsersArticles" (
    "article_id" INTEGER NOT NULL,
    "source_id" INTEGER NOT NULL,
    "url" TEXT NOT NULL,
    "user_id" INTEGER NOT NULL,

    CONSTRAINT "UsersArticles_pkey" PRIMARY KEY ("user_id","article_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "UsersArticles_article_id_url_key" ON "UsersArticles"("article_id", "url");

-- CreateIndex
CREATE UNIQUE INDEX "NewsArticles_id_url_key" ON "NewsArticles"("id", "url");

-- AddForeignKey
ALTER TABLE "UsersArticles" ADD CONSTRAINT "UsersArticles_article_id_url_fkey" FOREIGN KEY ("article_id", "url") REFERENCES "NewsArticles"("id", "url") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UsersArticles" ADD CONSTRAINT "UsersArticles_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "NewsSources"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UsersArticles" ADD CONSTRAINT "UsersArticles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "Users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
