/*
  Warnings:

  - You are about to drop the `Labels` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "NewsArticleLabels" DROP CONSTRAINT "NewsArticleLabels_label_fkey";

-- DropTable
DROP TABLE "Labels";
