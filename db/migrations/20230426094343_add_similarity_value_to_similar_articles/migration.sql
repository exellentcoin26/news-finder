/*
  Warnings:

  - You are about to drop the `Labels` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `similarity` to the `SimilarArticles` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "NewsArticleLabels" DROP CONSTRAINT "NewsArticleLabels_label_fkey";

-- AlterTable
ALTER TABLE "SimilarArticles" ADD COLUMN     "similarity" DOUBLE PRECISION NOT NULL;

-- DropTable
DROP TABLE "Labels";
