/*
  Warnings:

  - You are about to drop the column `usersArticlesSource_id` on the `NewsArticles` table. All the data in the column will be lost.
  - You are about to drop the column `usersArticlesUser_id` on the `NewsArticles` table. All the data in the column will be lost.

*/
-- DropForeignKey
ALTER TABLE "NewsArticles" DROP CONSTRAINT "NewsArticles_usersArticlesUser_id_usersArticlesSource_id_fkey";

-- AlterTable
ALTER TABLE "NewsArticles" DROP COLUMN "usersArticlesSource_id",
DROP COLUMN "usersArticlesUser_id";

-- AlterTable
ALTER TABLE "UsersArticles" ADD COLUMN     "newsArticlesId" INTEGER;

-- AddForeignKey
ALTER TABLE "UsersArticles" ADD CONSTRAINT "UsersArticles_newsArticlesId_fkey" FOREIGN KEY ("newsArticlesId") REFERENCES "NewsArticles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
