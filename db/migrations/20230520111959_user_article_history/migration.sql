/*
  Warnings:

  - A unique constraint covering the columns `[id,url]` on the table `NewsArticles` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateTable
CREATE TABLE "UserArticleHistory" (
    "labels" TEXT[],
    "source_url" TEXT NOT NULL,
    "user_id" INTEGER NOT NULL,
    "newsArticlesId" INTEGER,

    CONSTRAINT "UserArticleHistory_pkey" PRIMARY KEY ("user_id","source_url")
);

-- CreateIndex
CREATE UNIQUE INDEX "NewsArticles_id_url_key" ON "NewsArticles"("id", "url");

-- AddForeignKey
ALTER TABLE "UserArticleHistory" ADD CONSTRAINT "UserArticleHistory_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserArticleHistory" ADD CONSTRAINT "UserArticleHistory_newsArticlesId_fkey" FOREIGN KEY ("newsArticlesId") REFERENCES "NewsArticles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
