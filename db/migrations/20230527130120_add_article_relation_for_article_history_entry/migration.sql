/*
  Warnings:

  - You are about to drop the column `newsArticlesId` on the `UserArticleHistory` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[user_id,source_url,article_id]` on the table `UserArticleHistory` will be added. If there are existing duplicate values, this will fail.

*/
-- DropForeignKey
ALTER TABLE "UserArticleHistory" DROP CONSTRAINT "UserArticleHistory_newsArticlesId_fkey";

-- AlterTable
ALTER TABLE "UserArticleHistory" DROP COLUMN "newsArticlesId",
ADD COLUMN     "article_id" INTEGER;

-- CreateIndex
CREATE UNIQUE INDEX "UserArticleHistory_user_id_source_url_article_id_key" ON "UserArticleHistory"("user_id", "source_url", "article_id");

-- AddForeignKey
ALTER TABLE "UserArticleHistory" ADD CONSTRAINT "UserArticleHistory_article_id_fkey" FOREIGN KEY ("article_id") REFERENCES "NewsArticles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
