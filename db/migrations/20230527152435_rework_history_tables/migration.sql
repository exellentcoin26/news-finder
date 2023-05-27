/*
  Warnings:

  - The primary key for the `UserArticleHistory` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `labels` on the `UserArticleHistory` table. All the data in the column will be lost.
  - You are about to drop the column `source_url` on the `UserArticleHistory` table. All the data in the column will be lost.
  - Made the column `article_id` on table `UserArticleHistory` required. This step will fail if there are existing NULL values in that column.

*/
-- DropForeignKey
ALTER TABLE "UserArticleHistory" DROP CONSTRAINT "UserArticleHistory_article_id_fkey";

-- DropIndex
DROP INDEX "UserArticleHistory_user_id_source_url_article_id_key";

-- AlterTable
ALTER TABLE "UserArticleHistory" DROP CONSTRAINT "UserArticleHistory_pkey",
DROP COLUMN "labels",
DROP COLUMN "source_url",
ALTER COLUMN "article_id" SET NOT NULL,
ADD CONSTRAINT "UserArticleHistory_pkey" PRIMARY KEY ("user_id", "article_id");

-- CreateTable
CREATE TABLE "UserLabelSourceHistory" (
    "user_id" INTEGER NOT NULL,
    "labels" TEXT[],
    "source_url" TEXT NOT NULL,

    CONSTRAINT "UserLabelSourceHistory_pkey" PRIMARY KEY ("user_id")
);

-- AddForeignKey
ALTER TABLE "UserLabelSourceHistory" ADD CONSTRAINT "UserLabelSourceHistory_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "Users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserArticleHistory" ADD CONSTRAINT "UserArticleHistory_article_id_fkey" FOREIGN KEY ("article_id") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
